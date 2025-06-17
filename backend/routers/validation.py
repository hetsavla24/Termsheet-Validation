from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging
import uuid
import json
import os
from fastapi.responses import FileResponse

# Internal imports
try:
    from mongodb_models import (
        User as MongoUser,
        UploadedFile as MongoUploadedFile, 
        ValidationSession as MongoValidationSession,
        MasterTemplate as MongoMasterTemplate,
        UserActivity as MongoUserActivity,
        TradeRecord as MongoTradeRecord
    )
    from mongodb_dependencies import get_current_active_user, get_current_active_user_optional
    HAS_MONGODB = True
except ImportError:
    # Mock classes for when MongoDB is not available
    class MongoUser:
        def __init__(self):
            self.id = "mock_user_id"
            self.username = "mock_user"
    
    class MongoUploadedFile:
        def __init__(self):
            self.id = "mock_file_id"
    
    def get_current_active_user_optional():
        return MongoUser()
    
    def get_current_active_user():
        return MongoUser()
    
    HAS_MONGODB = False

from schemas import (
    MasterTemplateCreate,
    ValidationSessionCreate,
    ValidationSessionResponse,
    TemplateResponse,
    SuccessResponse,
    TradeRecordCreate,
    TradeRecordResponse,
    ValidationInterfaceData,
    ValidationSessionStartRequest,
    ValidationDecisionCreate,
    ValidationDecisionResponse,
    TermSheetDataResponse,
    ValidationDiscrepancyResponse,
    ProcessingStatus,
    ActivityType
)

router = APIRouter(prefix="/validation", tags=["validation"])

# In-memory storage for sessions when MongoDB is not available
SESSIONS_STORAGE = {}
TRADE_RECORDS_STORAGE = {}

@router.get("/status")
async def get_validation_status():
    """Get validation system status"""
    return {
        "status": "active",
        "mongodb_available": HAS_MONGODB,
        "sessions_count": len(SESSIONS_STORAGE) if not HAS_MONGODB else "N/A (using MongoDB)",
        "trade_records_count": len(TRADE_RECORDS_STORAGE) if not HAS_MONGODB else "N/A (using MongoDB)",
        "endpoints": {
            "auto_create_session": "/api/validation/sessions/auto-create",
            "create_session": "/api/validation/sessions",
            "list_sessions": "/api/validation/sessions",
            "get_session": "/api/validation/sessions/{session_id}"
        }
    }

@router.post("/sessions/auto-create", response_model=ValidationSessionResponse, status_code=status.HTTP_201_CREATED)
async def auto_create_validation_session(
    trade_id: str,
    session_name: Optional[str] = None,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Automatically create a validation session for a trade ID"""
    try:
        # Generate session name if not provided
        if not session_name:
            session_name = f"Auto Validation - {trade_id} - {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        session_id = str(uuid.uuid4())
        
        # Create session data (without requiring a file)
        session_data = {
            "id": session_id,
            "session_name": session_name,
            "file_id": None,  # Allow sessions without files for manual entry
            "template_id": None,
            "user_id": str(current_user.id) if current_user else "mock_user",
            "validation_type": "standard",
            "validation_rules": {},
            "status": "pending",
            "progress_percentage": 0,
            "validation_results": None,
            "error_count": 0,
            "warning_count": 0,
            "compliance_score": None,
            "created_by": current_user.username if current_user else "system",
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "completed_at": None,
            "trade_id": trade_id
        }
        
        if HAS_MONGODB:
            # Store in MongoDB if available
            session = MongoValidationSession(
                session_name=session_name,
                file_id=None,  # Allow sessions without files
                template_id=None,
                user_id=str(current_user.id),
                validation_type="standard",
                status=ProcessingStatus.PENDING,
                progress_percentage=0,
                session_configuration={},
                created_by=current_user.username,
                validation_results=None,
                error_count=0,
                warning_count=0,
                compliance_score=None,
                created_at=datetime.utcnow()
            )
            await session.insert()
            session_data["id"] = str(session.id)
        else:
            # Store in memory if MongoDB is not available
            SESSIONS_STORAGE[session_id] = session_data
        
        return ValidationSessionResponse(**session_data)
        
    except Exception as e:
        logging.error(f"Error auto-creating validation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-create validation session: {str(e)}"
        )

@router.post("/sessions", response_model=ValidationSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_validation_session(
    session_data: ValidationSessionCreate,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Create a new validation session"""
    try:
        session_id = str(uuid.uuid4())
        
        # Create session response data
        response_data = {
            "id": session_id,
            "session_name": session_data.session_name,
            "file_id": session_data.file_id,  # Can be None
            "template_id": session_data.template_id,
            "user_id": str(current_user.id) if current_user else "mock_user",
            "validation_type": session_data.validation_type or "standard",
            "validation_rules": session_data.validation_rules or {},
            "status": "pending",
            "progress_percentage": 0,
            "validation_results": None,
            "error_count": 0,
            "warning_count": 0,
            "compliance_score": None,
            "created_by": current_user.username if current_user else "system",
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "completed_at": None
        }
        
        if HAS_MONGODB:
            # MongoDB validation logic
            file = None
            if session_data.file_id:
                if not ObjectId.is_valid(session_data.file_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid file ID format"
                    )
                
                file = await MongoUploadedFile.find_one(
                    MongoUploadedFile.id == ObjectId(session_data.file_id),
                    MongoUploadedFile.user_id == str(current_user.id)  # Convert ObjectId to string
                )
                
                if not file:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="File not found"
                    )
            
            # Validate template exists if provided
            if session_data.template_id:
                if not ObjectId.is_valid(session_data.template_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid template ID format"
                    )
                
                template = await MongoMasterTemplate.find_one(
                    MongoMasterTemplate.id == ObjectId(session_data.template_id)
                )
                
                if not template:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Template not found"
                    )
            
            # Create validation session in MongoDB
            session = MongoValidationSession(
                session_name=session_data.session_name,
                file_id=session_data.file_id,  # Keep as string, since it's now optional
                template_id=session_data.template_id,
                user_id=str(current_user.id),
                validation_type=session_data.validation_type or "standard",
                status=ProcessingStatus.PENDING,
                progress_percentage=0,
                session_configuration=session_data.validation_rules or {},  # Store validation rules here
                created_by=current_user.username,
                validation_results=None,
                error_count=0,
                warning_count=0,
                compliance_score=None,
                created_at=datetime.utcnow()
            )
            
            await session.insert()
            response_data["id"] = str(session.id)
            response_data["file_id"] = session_data.file_id  # Update response with the actual file_id (could be None)
            
            # Log user activity
            activity = MongoUserActivity(
                user_id=str(current_user.id),  # Convert ObjectId to string
                activity_type=ActivityType.VALIDATION_SESSION_CREATED,
                description=f"Created validation session: {session_data.session_name}",
                activity_metadata={  # Use correct field name
                    "session_id": str(session.id),
                    "file_id": session_data.file_id,
                    "template_id": session_data.template_id,
                    "has_file": session_data.file_id is not None
                },
                timestamp=datetime.utcnow()
            )
            await activity.insert()
        else:
            # Store in memory for development without MongoDB
            SESSIONS_STORAGE[session_id] = response_data
            logging.info(f"Created session in memory: {session_id}")
        
        return ValidationSessionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating validation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during session creation"
        )

@router.get("/sessions", response_model=List[ValidationSessionResponse])
async def get_validation_sessions(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Get user's validation sessions"""
    try:
        session_responses = []
        
        if HAS_MONGODB:
            # Build query for MongoDB
            query = {"user_id": str(current_user.id)}  # Convert ObjectId to string
            if status_filter:
                query["status"] = status_filter
            
            # Get sessions with pagination from MongoDB
            sessions = await MongoValidationSession.find(query).skip(skip).limit(limit).to_list()
            
            for session in sessions:
                session_responses.append(ValidationSessionResponse(
                    id=str(session.id),
                    session_name=session.session_name,
                    file_id=str(session.file_id),
                    template_id=str(session.template_id) if session.template_id else None,
                    user_id=str(session.user_id),
                    validation_type=session.validation_type,
                    validation_rules=session.validation_rules,
                    status=session.status,
                    progress_percentage=session.progress_percentage,
                    validation_results=session.validation_results,
                    error_count=session.error_count,
                    warning_count=session.warning_count,
                    compliance_score=session.compliance_score,
                    created_by=session.created_by,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    completed_at=session.completed_at
                ))
        else:
            # Get sessions from in-memory storage
            sessions = list(SESSIONS_STORAGE.values())
            
            # Apply filters
            if status_filter:
                sessions = [s for s in sessions if s.get("status") == status_filter]
            
            # Apply pagination
            sessions = sessions[skip:skip + limit]
            
            for session in sessions:
                session_responses.append(ValidationSessionResponse(**session))
        
        return session_responses
        
    except Exception as e:
        logging.error(f"Error getting validation sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching sessions"
        )

@router.get("/sessions/{session_id}", response_model=ValidationSessionResponse)
async def get_validation_session(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Get details of a specific validation session"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        # Find session
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        return ValidationSessionResponse(
            id=str(session.id),
            session_name=session.session_name,
            file_id=str(session.file_id),
            template_id=str(session.template_id) if session.template_id else None,
            user_id=str(session.user_id),
            validation_type=session.validation_type,
            validation_rules=session.validation_rules,
            status=session.status,
            progress_percentage=session.progress_percentage,
            validation_results=session.validation_results,
            error_count=session.error_count,
            warning_count=session.warning_count,
            compliance_score=session.compliance_score,
            created_by=session.created_by,
            created_at=session.created_at,
            updated_at=session.updated_at,
            completed_at=session.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting validation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching session"
        )

@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: MasterTemplateCreate,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Create a new validation template"""
    try:
        template = MongoMasterTemplate(
            template_name=template_data.template_name,
            description=template_data.description,
            template_type=template_data.template_type,
            validation_rules=template_data.validation_rules,
            expected_columns=template_data.expected_columns,
            required_columns=template_data.required_columns,
            data_types=template_data.data_types,
            validation_constraints=template_data.validation_constraints,
            is_active=template_data.is_active,
            created_by=current_user.username,
            created_at=datetime.utcnow()
        )
        
        await template.insert()
        
        # Log user activity
        activity = MongoUserActivity(
            user_id=str(current_user.id),  # Convert ObjectId to string
            activity_type=ActivityType.TEMPLATE_CREATE,
            description=f"Created validation template: {template_data.template_name}",
            activity_metadata={  # Use correct field name
                "template_id": str(template.id),
                "template_name": template_data.template_name
            },
            timestamp=datetime.utcnow()
        )
        await activity.insert()
        
        return TemplateResponse(
            id=str(template.id),
            template_name=template.template_name,
            description=template.description,
            template_type=template.template_type,
            validation_rules=template.validation_rules,
            expected_columns=template.expected_columns,
            required_columns=template.required_columns,
            data_types=template.data_types,
            validation_constraints=template.validation_constraints,
            is_active=template.is_active,
            usage_count=template.usage_count,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except Exception as e:
        logging.error(f"Error creating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during template creation"
        )

@router.get("/templates/public", response_model=List[TemplateResponse])
async def get_public_templates(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True
):
    """Get validation templates (public endpoint)"""
    try:
        # Build query
        query = {}
        if active_only:
            query["is_active"] = True
        
        # Get templates with pagination
        templates = await MongoMasterTemplate.find(query).skip(skip).limit(limit).to_list()
        
        template_responses = []
        for template in templates:
            template_responses.append(TemplateResponse(
                id=str(template.id),
                template_name=template.template_name,
                description=template.description,
                template_type=getattr(template, 'template_type', 'standard'),  # Default if not present
                validation_rules=template.validation_rules[0] if template.validation_rules else None,  # Convert list to dict for compatibility
                expected_columns=getattr(template, 'expected_columns', None),
                required_columns=getattr(template, 'required_columns', None),
                data_types=getattr(template, 'data_types', None),
                validation_constraints=getattr(template, 'validation_constraints', None),
                is_active=template.is_active,
                usage_count=template.usage_count,
                created_by=template.created_by,
                created_at=template.created_at,
                updated_at=getattr(template, 'updated_at', None)
            ))
        
        return template_responses
        
    except Exception as e:
        logging.error(f"Error getting public templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching templates"
        )

@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    skip: int = 0,
    limit: int = 20,
    active_only: bool = True,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Get validation templates (authenticated endpoint with user context)"""
    try:
        # Build query
        query = {}
        if active_only:
            query["is_active"] = True
        
        # Get templates with pagination
        templates = await MongoMasterTemplate.find(query).skip(skip).limit(limit).to_list()
        
        template_responses = []
        for template in templates:
            template_responses.append(TemplateResponse(
                id=str(template.id),
                template_name=template.template_name,
                description=template.description,
                template_type=getattr(template, 'template_type', 'standard'),  # Default if not present
                validation_rules=template.validation_rules[0] if template.validation_rules else None,  # Convert list to dict for compatibility
                expected_columns=getattr(template, 'expected_columns', None),
                required_columns=getattr(template, 'required_columns', None),
                data_types=getattr(template, 'data_types', None),
                validation_constraints=getattr(template, 'validation_constraints', None),
                is_active=template.is_active,
                usage_count=template.usage_count,
                created_by=template.created_by,
                created_at=template.created_at,
                updated_at=getattr(template, 'updated_at', None)
            ))
        
        return template_responses
        
    except Exception as e:
        logging.error(f"Error getting templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching templates"
        )

@router.post("/trade-records", response_model=TradeRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_trade_record(
    trade_data: TradeRecordCreate,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Create a new trade record for validation comparison"""
    try:
        # Check if trade ID already exists
        existing_trade = await MongoTradeRecord.find_one({"trade_id": trade_data.trade_id})
        
        if existing_trade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trade ID already exists"
            )
        
        trade_record = MongoTradeRecord(
            **trade_data.dict(),
            created_by=current_user.username
        )
        
        await trade_record.insert()
        
        return TradeRecordResponse(
            id=str(trade_record.id),
            **trade_data.dict(),
            status=trade_record.status,
            created_by=trade_record.created_by,
            created_at=trade_record.created_at,
            updated_at=trade_record.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating trade record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during trade record creation"
        )

@router.get("/trade-records/{trade_id}", response_model=TradeRecordResponse)
async def get_trade_record(
    trade_id: str,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Get trade record by trade ID"""
    try:
        try:
            trade_record = await MongoTradeRecord.find_one({"trade_id": trade_id})
        except Exception as e:
            # Fallback to mock data for testing/development
            logging.warning(f"Database query failed, using mock data: {e}")
            mock_records = {
                "TR-2025-0420": {
                    "_id": "507f1f77bcf86cd799439011",
                    "trade_id": "TR-2025-0420",
                    "counterparty": "HSBC Bank plc",
                    "notional_amount": 25000000.0,
                    "settlement_date": "2025-03-15T00:00:00Z",
                    "interest_rate": 4.25,
                    "currency": "USD",
                    "payment_terms": "Quarterly",
                    "legal_entity": "HSBC Holdings plc London Branch",
                    "trade_type": "Interest Rate Swap",
                    "maturity_date": "2027-03-15T00:00:00Z",
                    "reference_rate": "SOFR + 1.50%",
                    "status": "active",
                    "created_by": "system",
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": None
                }
            }
            
            if trade_id in mock_records:
                # Convert mock data to object with attributes
                class MockRecord:
                    def __init__(self, data):
                        for key, value in data.items():
                            if key == "_id":
                                self.id = value
                            else:
                                setattr(self, key, value)
                        # Convert date strings to datetime for consistency
                        from datetime import datetime
                        if isinstance(self.settlement_date, str):
                            self.settlement_date = datetime.fromisoformat(self.settlement_date.replace('Z', '+00:00'))
                        if hasattr(self, 'maturity_date') and isinstance(self.maturity_date, str):
                            self.maturity_date = datetime.fromisoformat(self.maturity_date.replace('Z', '+00:00'))
                        if isinstance(self.created_at, str):
                            self.created_at = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
                
                trade_record = MockRecord(mock_records[trade_id])
            else:
                trade_record = None
        
        if not trade_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trade record not found"
            )
            
        return TradeRecordResponse(
            id=str(trade_record.id),
            trade_id=trade_record.trade_id,
            counterparty=trade_record.counterparty,
            notional_amount=trade_record.notional_amount,
            settlement_date=trade_record.settlement_date,
            interest_rate=trade_record.interest_rate,
            currency=trade_record.currency,
            payment_terms=trade_record.payment_terms,
            legal_entity=trade_record.legal_entity,
            trade_type=trade_record.trade_type,
            maturity_date=trade_record.maturity_date,
            reference_rate=trade_record.reference_rate,
            status=trade_record.status,
            created_by=trade_record.created_by,
            created_at=trade_record.created_at,
            updated_at=trade_record.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Error getting trade record: {e}")
        logging.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching trade record: {str(e)}"
        )

@router.get("/trade-records", response_model=List[TradeRecordResponse])
async def list_trade_records(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """List available trade records for validation"""
    try:
        # Build query
        query = {}
        if status_filter:
            query["status"] = status_filter
        else:
            # Default to active records only
            query["status"] = "active"
        
        # Get trade records with pagination
        try:
            trade_records = await MongoTradeRecord.find(query).skip(skip).limit(limit).to_list()
        except Exception as e:
            # Fallback to mock data for testing/development
            logging.warning(f"Database query failed, using mock data: {e}")
            mock_records = [
                {
                    "_id": "507f1f77bcf86cd799439011",
                    "trade_id": "TR-2025-0420",
                    "counterparty": "HSBC Bank plc",
                    "notional_amount": 25000000.0,
                    "settlement_date": "2025-03-15T00:00:00Z",
                    "interest_rate": 4.25,
                    "currency": "USD",
                    "payment_terms": "Quarterly",
                    "legal_entity": "HSBC Holdings plc London Branch",
                    "trade_type": "Interest Rate Swap",
                    "maturity_date": "2027-03-15T00:00:00Z",
                    "reference_rate": "SOFR + 1.50%",
                    "status": "active",
                    "created_by": "system",
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": None
                },
                {
                    "_id": "507f1f77bcf86cd799439012",
                    "trade_id": "TR-2025-0421",
                    "counterparty": "Goldman Sachs",
                    "notional_amount": 50000000.0,
                    "settlement_date": "2025-03-20T00:00:00Z",
                    "interest_rate": 4.50,
                    "currency": "USD",
                    "payment_terms": "Quarterly",
                    "legal_entity": "Goldman Sachs & Co. LLC",
                    "trade_type": "Interest Rate Swap",
                    "maturity_date": "2027-03-20T00:00:00Z",
                    "reference_rate": "SOFR + 1.75%",
                    "status": "active",
                    "created_by": "system",
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": None
                }
            ]
            
            # Convert mock data to objects with attributes
            class MockRecord:
                def __init__(self, data):
                    for key, value in data.items():
                        if key == "_id":
                            self.id = value
                        else:
                            setattr(self, key, value)
                    # Convert date strings to datetime for consistency
                    from datetime import datetime
                    if isinstance(self.settlement_date, str):
                        self.settlement_date = datetime.fromisoformat(self.settlement_date.replace('Z', '+00:00'))
                    if hasattr(self, 'maturity_date') and isinstance(self.maturity_date, str):
                        self.maturity_date = datetime.fromisoformat(self.maturity_date.replace('Z', '+00:00'))
                    if isinstance(self.created_at, str):
                        self.created_at = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            
            trade_records = [MockRecord(record) for record in mock_records]
        
        return [
            TradeRecordResponse(
                id=str(record.id),
                trade_id=record.trade_id,
                counterparty=record.counterparty,
                notional_amount=record.notional_amount,
                settlement_date=record.settlement_date,
                interest_rate=record.interest_rate,
                currency=record.currency,
                payment_terms=record.payment_terms,
                legal_entity=record.legal_entity,
                trade_type=record.trade_type,
                maturity_date=record.maturity_date,
                reference_rate=record.reference_rate,
                status=record.status,
                created_by=record.created_by,
                created_at=record.created_at,
                updated_at=record.updated_at
            ) for record in trade_records
        ]
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Error listing trade records: {e}")
        logging.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching trade records: {str(e)}"
        )

@router.post("/sessions/{session_id}/start-validation", response_model=ValidationInterfaceData)
async def start_validation_interface(
    session_id: str,
    request: ValidationSessionStartRequest,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Start the validation interface process"""
    try:
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        # Start the AI processing and term extraction
        from nlp_engine import process_document_for_validation
        
        # Get the uploaded file
        file = await MongoUploadedFile.find_one(
            MongoUploadedFile.id == ObjectId(session.file_id)
        )
        
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated file not found"
            )
        
        # Extract term sheet data using NLP
        term_sheet_data = await process_document_for_validation(file.file_path, session_id)
        
        # Get matching trade record if trade_id provided
        trade_record = None
        if request.trade_id:
            trade_record = await MongoTradeRecord.find_one({"trade_id": request.trade_id})
        
        # Perform AI analysis and detect discrepancies
        validation_analysis = await perform_reference_validation(session_id, term_sheet_data, trade_record)
        
        # Update session status
        session.status = ProcessingStatus.PROCESSING
        await session.save()
        
        return ValidationInterfaceData(
            session=ValidationSessionResponse(
                id=str(session.id),
                session_name=session.session_name,
                file_id=str(session.file_id),
                template_id=str(session.template_id) if session.template_id else None,
                user_id=str(session.user_id),
                validation_type=session.validation_type,
                validation_rules=session.validation_rules,
                status=session.status,
                progress_percentage=session.progress_percentage,
                validation_results=session.validation_results,
                error_count=session.error_count,
                warning_count=session.warning_count,
                compliance_score=session.compliance_score,
                created_by=session.created_by,
                created_at=session.created_at,
                updated_at=session.updated_at,
                completed_at=session.completed_at
            ),
            term_sheet_data=term_sheet_data,
            trade_record=TradeRecordResponse(
                id=str(trade_record.id),
                trade_id=trade_record.trade_id,
                counterparty=trade_record.counterparty,
                notional_amount=trade_record.notional_amount,
                settlement_date=trade_record.settlement_date,
                interest_rate=trade_record.interest_rate,
                currency=trade_record.currency,
                payment_terms=trade_record.payment_terms,
                legal_entity=trade_record.legal_entity,
                trade_type=trade_record.trade_type,
                maturity_date=trade_record.maturity_date,
                reference_rate=trade_record.reference_rate,
                status=trade_record.status,
                created_by=trade_record.created_by,
                created_at=trade_record.created_at,
                updated_at=trade_record.updated_at
            ) if trade_record else None,
            validation_analysis=validation_analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error starting validation interface: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during validation interface startup"
        )

@router.get("/sessions/{session_id}/interface-data", response_model=ValidationInterfaceData)
async def get_validation_interface_data(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Get complete validation interface data"""
    try:
        logging.info(f"Fetching interface data for session: {session_id}")
        
        if not ObjectId.is_valid(session_id):
            logging.warning(f"Invalid session ID format: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        # Get session
        logging.info(f"Finding session with ID: {session_id}")
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not session:
            logging.warning(f"Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        logging.info(f"Found session: {session.session_name}")
        
        # Create the basic session response
        session_response = ValidationSessionResponse(
            id=str(session.id),
            session_name=session.session_name,
            file_id=str(session.file_id) if session.file_id else None,
            template_id=str(session.template_id) if session.template_id else None,
            user_id=str(session.user_id),
            validation_type=session.validation_type,
            validation_rules=session.validation_rules or {},  # Ensure we have a dict even if None
            status=session.status,
            progress_percentage=session.progress_percentage,
            validation_results=session.validation_results,
            error_count=session.error_count,
            warning_count=session.warning_count,
            compliance_score=session.compliance_score,
            created_by=session.created_by,
            created_at=session.created_at,
            updated_at=session.updated_at,
            completed_at=session.completed_at
        )
        
        # Create the basic interface data response with just the session
        response = ValidationInterfaceData(
            session=session_response,
            term_sheet_data=None,
            trade_record=None,
            discrepancies=[],
            validation_decision=None,
            validation_analysis={},
            compliance_status={}
        )
        
        # Try to get term sheet data
        term_sheet = None
        try:
            from mongodb_models import TermSheetData as MongoTermSheetData
            logging.info(f"Finding term sheet data for session: {session_id}")
            term_sheet = await MongoTermSheetData.find_one({"session_id": session_id})
            logging.info(f"Term sheet data found: {term_sheet is not None}")
            
            if term_sheet:
                response.term_sheet_data = TermSheetDataResponse(
                    id=str(term_sheet.id),
                    session_id=term_sheet.session_id,
                    trade_id=term_sheet.trade_id,
                    counterparty=term_sheet.counterparty,
                    notional_amount=term_sheet.notional_amount,
                    settlement_date=term_sheet.settlement_date,
                    interest_rate=term_sheet.interest_rate,
                    currency=term_sheet.currency,
                    payment_terms=term_sheet.payment_terms,
                    legal_entity=term_sheet.legal_entity,
                    extraction_confidence=term_sheet.extraction_confidence,
                    extraction_source=term_sheet.extraction_source,
                    created_at=term_sheet.created_at,
                    updated_at=term_sheet.updated_at
                )
        except Exception as e:
            logging.error(f"Error fetching term sheet data: {e}")
        
        # Try to get trade record if term sheet has trade_id
        if term_sheet and term_sheet.trade_id:
            try:
                logging.info(f"Finding trade record with ID: {term_sheet.trade_id}")
                trade_record = await MongoTradeRecord.find_one({"trade_id": term_sheet.trade_id})
                logging.info(f"Trade record found: {trade_record is not None}")
                
                if trade_record:
                    response.trade_record = TradeRecordResponse(
                        id=str(trade_record.id),
                        trade_id=trade_record.trade_id,
                        counterparty=trade_record.counterparty,
                        notional_amount=trade_record.notional_amount,
                        settlement_date=trade_record.settlement_date,
                        interest_rate=trade_record.interest_rate,
                        currency=trade_record.currency,
                        payment_terms=trade_record.payment_terms,
                        legal_entity=trade_record.legal_entity,
                        trade_type=trade_record.trade_type,
                        maturity_date=trade_record.maturity_date,
                        reference_rate=trade_record.reference_rate,
                        status=trade_record.status,
                        created_by=trade_record.created_by,
                        created_at=trade_record.created_at,
                        updated_at=trade_record.updated_at
                    )
            except Exception as e:
                logging.error(f"Error fetching trade record: {e}")
        
        # Try to get discrepancies
        try:
            from mongodb_models import ValidationDiscrepancy as MongoValidationDiscrepancy
            logging.info(f"Finding discrepancies for session: {session_id}")
            discrepancies = await MongoValidationDiscrepancy.find(
                MongoValidationDiscrepancy.session_id == session_id
            ).to_list()
            logging.info(f"Found {len(discrepancies)} discrepancies")
            
            if discrepancies:
                response.discrepancies = [
                    ValidationDiscrepancyResponse(
                        id=str(d.id),
                        session_id=d.session_id,
                        discrepancy_type=d.discrepancy_type,
                        field_name=d.field_name,
                        term_sheet_value=d.term_sheet_value,
                        trade_record_value=d.trade_record_value,
                        confidence_score=d.confidence_score,
                        impact_level=d.impact_level,
                        description=d.description,
                        recommendation=d.recommendation,
                        status=d.status,
                        resolved_by=d.resolved_by,
                        resolved_at=d.resolved_at,
                        created_at=d.created_at
                    ) for d in discrepancies
                ]
        except Exception as e:
            logging.error(f"Error fetching discrepancies: {e}")
        
        # Try to get validation decision
        try:
            from mongodb_models import ValidationDecision as MongoValidationDecision
            logging.info(f"Finding validation decision for session: {session_id}")
            decision = await MongoValidationDecision.find_one(
                MongoValidationDecision.session_id == session_id
            )
            logging.info(f"Decision found: {decision is not None}")
            
            if decision:
                response.validation_decision = ValidationDecisionResponse(
                    id=str(decision.id),
                    session_id=decision.session_id,
                    decision=decision.decision,
                    decision_reason=decision.decision_reason,
                    ai_risk_score=decision.ai_risk_score,
                    mifid_status=decision.mifid_status,
                    fca_status=decision.fca_status,
                    sec_status=decision.sec_status,
                    total_discrepancies=decision.total_discrepancies,
                    critical_issues=decision.critical_issues,
                    minor_issues=decision.minor_issues,
                    decided_by=decision.decided_by,
                    decided_at=decision.decided_at
                )
        except Exception as e:
            logging.error(f"Error fetching validation decision: {e}")
        
        logging.info(f"Successfully built interface data response for session: {session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting validation interface data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching validation data: {str(e)}"
        )

@router.post("/sessions/{session_id}/decision", response_model=ValidationDecisionResponse)
async def make_validation_decision(
    session_id: str,
    decision_data: ValidationDecisionCreate,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Make a validation decision (approve, reject, manual_review)"""
    try:
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        # Get discrepancies count
        from mongodb_models import ValidationDiscrepancy as MongoValidationDiscrepancy
        discrepancies = await MongoValidationDiscrepancy.find(
            MongoValidationDiscrepancy.session_id == session_id
        ).to_list()
        
        critical_count = len([d for d in discrepancies if d.discrepancy_type == "critical"])
        minor_count = len([d for d in discrepancies if d.discrepancy_type == "minor"])
        
        # Calculate AI risk score based on discrepancies
        ai_risk_score = min(100, critical_count * 25 + minor_count * 10)
        
        # Determine compliance status
        mifid_status = "warning" if critical_count > 0 else "compliant"
        fca_status = "non_compliant" if critical_count > 2 else "compliant"
        sec_status = "non_compliant" if critical_count > 1 else "compliant"
        
        # Create validation decision
        from mongodb_models import ValidationDecision as MongoValidationDecision
        decision = MongoValidationDecision(
            session_id=session_id,
            decision=decision_data.decision,
            decision_reason=decision_data.decision_reason,
            ai_risk_score=ai_risk_score,
            mifid_status=mifid_status,
            fca_status=fca_status,
            sec_status=sec_status,
            total_discrepancies=len(discrepancies),
            critical_issues=critical_count,
            minor_issues=minor_count,
            decided_by=current_user.username
        )
        
        await decision.insert()
        
        # Update session status based on decision type
        if decision_data.decision == "approve":
            session.status = ProcessingStatus.COMPLETED
        elif decision_data.decision == "reject":
            session.status = ProcessingStatus.FAILED
        elif decision_data.decision == "manual_review":
            session.status = "manual_review"  # Custom status for manual review
        else:
            session.status = ProcessingStatus.COMPLETED  # Default to completed
            
        session.completed_at = datetime.utcnow()
        await session.save()
        
        # Log user activity
        activity = MongoUserActivity(
            user_id=str(current_user.id),
            activity_type=ActivityType.VALIDATION_COMPLETE,
            description=f"Made validation decision: {decision_data.decision}",
            activity_metadata={
                "session_id": session_id,
                "decision": decision_data.decision,
                "status": session.status
            }
        )
        await activity.insert()
        
        return ValidationDecisionResponse(
            id=str(decision.id),
            session_id=decision.session_id,
            decision=decision.decision,
            decision_reason=decision.decision_reason,
            ai_risk_score=decision.ai_risk_score,
            mifid_status=decision.mifid_status,
            fca_status=decision.fca_status,
            sec_status=decision.sec_status,
            total_discrepancies=decision.total_discrepancies,
            critical_issues=decision.critical_issues,
            minor_issues=decision.minor_issues,
            decided_by=decision.decided_by,
            decided_at=decision.decided_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error making validation decision: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during decision making"
        )

# Helper function for reference-based validation
async def perform_reference_validation(session_id: str, term_sheet_data, trade_record):
    """Perform validation using reference files and validation rules"""
    try:
        from mongodb_models import ValidationDiscrepancy as MongoValidationDiscrepancy
        import json
        from pathlib import Path
        
        discrepancies = []
        total_risk_score = 0
        
        # Load validation rules from reference file
        try:
            rules_file = Path("../uploads/reference/validation_rules_reference.json")
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    validation_config = json.load(f)
            else:
                validation_config = {
                    "validation_rules": {
                        "notional_amount": {"tolerance": 0.05, "critical_threshold": 0.1, "data_type": "numeric"},
                        "interest_rate": {"tolerance": 0.25, "critical_threshold": 0.5, "data_type": "numeric"}
                    },
                    "risk_scoring": {"critical_discrepancy": 25, "minor_discrepancy": 10}
                }
        except Exception:
            validation_config = {"validation_rules": {}, "risk_scoring": {"critical_discrepancy": 25, "minor_discrepancy": 10}}
        
        if term_sheet_data and trade_record:
            # Field comparisons with reference-based validation
            field_comparisons = [
                ("counterparty", getattr(term_sheet_data, 'counterparty', None), trade_record.counterparty),
                ("notional_amount", getattr(term_sheet_data, 'notional_amount', None), str(trade_record.notional_amount)),
                ("settlement_date", getattr(term_sheet_data, 'settlement_date', None), trade_record.settlement_date.strftime("%Y-%m-%d")),
                ("interest_rate", getattr(term_sheet_data, 'interest_rate', None), str(trade_record.interest_rate)),
                ("currency", getattr(term_sheet_data, 'currency', None), trade_record.currency),
                ("payment_terms", getattr(term_sheet_data, 'payment_terms', None), trade_record.payment_terms),
                ("legal_entity", getattr(term_sheet_data, 'legal_entity', None), trade_record.legal_entity)
            ]
            
            for field_name, ts_value, tr_value in field_comparisons:
                if ts_value and tr_value:
                    validation_result = await validate_field_with_rules(
                        field_name, ts_value, tr_value, validation_config
                    )
                    
                    if not validation_result["is_valid"]:
                        discrepancy = MongoValidationDiscrepancy(
                            session_id=session_id,
                            discrepancy_type=validation_result["discrepancy_type"],
                            field_name=field_name,
                            term_sheet_value=str(ts_value),
                            trade_record_value=str(tr_value),
                            confidence_score=0.95,
                            impact_level="high" if validation_result["discrepancy_type"] == "critical" else "medium",
                            description=validation_result["description"],
                            recommendation=f"Review and verify the {field_name.replace('_', ' ')} value according to validation rules"
                        )
                        
                        await discrepancy.insert()
                        discrepancies.append(discrepancy)
                        total_risk_score += validation_result["risk_score"]
        
        return {
            "detected_discrepancies": len(discrepancies),
            "total_risk_score": min(total_risk_score, 100),
            "analysis_complete": True,
            "risk_level": "high" if total_risk_score > 50 else "medium" if total_risk_score > 20 else "low",
            "validation_method": "reference_based"
        }
        
    except Exception as e:
        logging.error(f"Error in reference validation: {e}")
        return {"error": "Reference validation failed", "detected_discrepancies": 0}

async def validate_field_with_rules(field_name: str, ts_value, tr_value, config: dict):
    """Validate field using reference rules"""
    rules = config.get("validation_rules", {})
    scoring = config.get("risk_scoring", {})
    
    if field_name not in rules:
        # Default comparison
        if str(ts_value).strip().lower() == str(tr_value).strip().lower():
            return {"is_valid": True, "discrepancy_type": None, "risk_score": 0, "description": f"{field_name} values match"}
        else:
            return {"is_valid": False, "discrepancy_type": "minor", "risk_score": scoring.get("minor_discrepancy", 10), "description": f"{field_name} values differ"}
    
    rule = rules[field_name]
    data_type = rule.get("data_type", "string")
    
    if data_type == "numeric":
        try:
            # Parse numeric values
            ts_str = str(ts_value).replace('$', '').replace(',', '').strip()
            tr_str = str(tr_value).replace('$', '').replace(',', '').strip()
            
            ts_num = float(ts_str.split()[0])
            tr_num = float(tr_str)
            
            tolerance = rule.get("tolerance", 0.05)
            critical_threshold = rule.get("critical_threshold", 0.1)
            
            diff_percent = abs(ts_num - tr_num) / tr_num if tr_num != 0 else float('inf')
            
            if diff_percent <= tolerance:
                return {"is_valid": True, "discrepancy_type": None, "risk_score": 0, "description": f"{field_name} within acceptable tolerance"}
            elif diff_percent <= critical_threshold:
                return {"is_valid": False, "discrepancy_type": "minor", "risk_score": scoring.get("minor_discrepancy", 10), "description": f"{field_name} minor discrepancy: {diff_percent:.2%} difference"}
            else:
                return {"is_valid": False, "discrepancy_type": "critical", "risk_score": scoring.get("critical_discrepancy", 25), "description": f"{field_name} critical discrepancy: {diff_percent:.2%} difference"}
        except Exception:
            return {"is_valid": False, "discrepancy_type": "error", "risk_score": 5, "description": f"{field_name} format error"}
    else:
        # String comparison
        if str(ts_value).strip().lower() == str(tr_value).strip().lower():
            return {"is_valid": True, "discrepancy_type": None, "risk_score": 0, "description": f"{field_name} values match"}
        else:
            return {"is_valid": False, "discrepancy_type": "minor", "risk_score": scoring.get("minor_discrepancy", 10), "description": f"{field_name} values differ"}

# Legacy endpoints for frontend compatibility
@router.post("/validate/{session_id}")
async def validate_termsheet_legacy(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Legacy endpoint - validate termsheet (redirects to start-validation)"""
    try:
        # For backwards compatibility, redirect to the new endpoint
        return await start_validation_interface(
            session_id=session_id,
            request=ValidationSessionStartRequest(trade_id=None),
            current_user=current_user
        )
    except Exception as e:
        logging.error(f"Error in legacy validate endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during validation"
        )

@router.get("/results/{session_id}")
async def get_validation_results_legacy(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Legacy endpoint - get validation results"""
    try:
        # Get validation session
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        return {
            "session_id": session_id,
            "status": session.status,
            "results": session.validation_results,
            "error_count": session.error_count,
            "warning_count": session.warning_count,
            "compliance_score": session.compliance_score,
            "completed_at": session.completed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting validation results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching results"
        )

@router.get("/report/{session_id}/{format}")
async def download_validation_report(
    session_id: str,
    format: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Download validation report in specified format"""
    try:
        if format not in ["pdf", "excel", "json"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supported formats: pdf, excel, json"
            )
        
        # Get validation session
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)  # Convert ObjectId to string
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        # Generate report based on format
        try:
            from validation_report import generate_validation_report
            report_content = await generate_validation_report(session, format)
        except ImportError:
            # Create a simple report if validation_report module is not available
            import tempfile
            import json as json_module
            
            report_data = {
                "session_id": session_id,
                "session_name": session.session_name,
                "status": session.status,
                "validation_results": session.validation_results,
                "error_count": session.error_count,
                "warning_count": session.warning_count,
                "compliance_score": session.compliance_score,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
            
            if format == "json":
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json_module.dump(report_data, temp_file, indent=2)
                temp_file.close()
                report_content = temp_file.name
            else:
                # For pdf/excel, create a simple text file
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                temp_file.write(f"Validation Report\n")
                temp_file.write(f"Session: {session.session_name}\n")
                temp_file.write(f"Status: {session.status}\n")
                temp_file.write(f"Errors: {session.error_count}\n")
                temp_file.write(f"Warnings: {session.warning_count}\n")
                temp_file.close()
                report_content = temp_file.name
        
        filename = f"validation_report_{session_id}.{format}"
        media_type = {
            "pdf": "application/pdf",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json"
        }[format]
        
        return FileResponse(
            path=report_content,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error generating validation report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while generating report"
        )

@router.get("/sessions/{session_id}/terms")
async def get_session_terms(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Get extracted terms from validation session"""
    try:
        # Get interface data which contains terms
        interface_data = await get_validation_interface_data(session_id, current_user)
        return {
            "session_id": session_id,
            "terms": interface_data.term_sheet_data,
            "extraction_status": "completed" if interface_data.term_sheet_data else "pending"
        }
    except Exception as e:
        logging.error(f"Error getting session terms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching terms"
        )

@router.get("/sessions/{session_id}/results")
async def get_session_results(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Get validation results for session"""
    try:
        # Redirect to legacy results endpoint
        return await get_validation_results_legacy(session_id, current_user)
    except Exception as e:
        logging.error(f"Error getting session results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching results"
        )

@router.get("/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Get validation session summary"""
    try:
        # Get validation session
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == current_user.id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        # Get associated file info
        file = await MongoUploadedFile.find_one(
            MongoUploadedFile.id == ObjectId(session.file_id)
        )
        
        return {
            "session_id": session_id,
            "session_name": session.session_name,
            "file_info": {
                "filename": file.filename if file else "Unknown",
                "file_size": file.file_size if file else 0
            },
            "status": session.status,
            "progress": session.progress_percentage,
            "validation_summary": {
                "total_terms": len(session.validation_results or []),
                "errors": session.error_count,
                "warnings": session.warning_count,
                "compliance_score": session.compliance_score
            },
            "created_at": session.created_at,
            "completed_at": session.completed_at,
            "processing_time": (session.completed_at - session.created_at).total_seconds() if session.completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting session summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching summary"
        )

# Test endpoint for debugging session creation
@router.post("/test-session", response_model=dict)
async def test_session_creation():
    """Test endpoint to create a simple validation session for debugging"""
    try:
        session_id = str(uuid.uuid4())
        
        # Create a simple session without complex dependencies
        test_session = {
            "id": session_id,
            "session_name": "Test Session",
            "file_id": None,
            "template_id": None,
            "user_id": "test_user",
            "validation_type": "standard",
            "validation_rules": {},
            "status": "pending",
            "progress_percentage": 0,
            "validation_results": None,
            "error_count": 0,
            "warning_count": 0,
            "compliance_score": None,
            "created_by": "test_user",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
            "completed_at": None
        }
        
        # Store in memory for testing
        SESSIONS_STORAGE[session_id] = test_session
        
        return {
            "message": "Test session created successfully",
            "session": test_session,
            "mongodb_available": HAS_MONGODB
        }
        
    except Exception as e:
        logging.error(f"Error in test session creation: {e}")
        return {
            "error": str(e),
            "message": "Test session creation failed",
            "mongodb_available": HAS_MONGODB
        }

@router.get("/health-check", response_model=SuccessResponse)
async def health_check():
    """Simple health check endpoint"""
    logging.info("Health check endpoint called")
    return SuccessResponse(message="Validation API is healthy")

@router.get("/sessions/{session_id}/basic-interface", response_model=ValidationInterfaceData)
async def get_basic_validation_interface(
    session_id: str,
    current_user: MongoUser = Depends(get_current_active_user_optional)
):
    """Get simplified validation interface data (for debugging)"""
    try:
        logging.info(f"Fetching basic interface data for session: {session_id}")
        
        # Create a basic session response with minimal data
        session_response = ValidationSessionResponse(
            id=session_id,
            session_name="Debug Session",
            file_id=None,
            template_id=None,
            user_id=str(current_user.id) if current_user else "debug_user",
            validation_type="standard",
            validation_rules={},
            status="pending",
            progress_percentage=0,
            validation_results=None,
            error_count=0,
            warning_count=0,
            compliance_score=None,
            created_by="system",
            created_at=datetime.utcnow(),
            updated_at=None,
            completed_at=None
        )
        
        # Create a minimal interface data response
        response = ValidationInterfaceData(
            session=session_response,
            term_sheet_data=None,
            trade_record=None,
            discrepancies=[],
            validation_decision=None,
            validation_analysis={},
            compliance_status={}
        )
        
        logging.info("Successfully built basic interface data response")
        return response
        
    except Exception as e:
        logging.error(f"Error getting basic validation interface data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.patch("/sessions/{session_id}/status", response_model=ValidationSessionResponse)
async def update_session_status(
    session_id: str,
    status_data: dict,
    current_user: MongoUser = Depends(get_current_active_user)
):
    """Update validation session status"""
    try:
        if not ObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        # Get session
        session = await MongoValidationSession.find_one(
            MongoValidationSession.id == ObjectId(session_id),
            MongoValidationSession.user_id == str(current_user.id)
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation session not found"
            )
        
        # Update status
        new_status = status_data.get('status')
        if new_status:
            session.status = new_status
            session.updated_at = datetime.utcnow()
            
            # If status is completed or failed, set completed_at
            if new_status in ['completed', 'failed']:
                session.completed_at = datetime.utcnow()
            
            await session.save()
            
            # Log user activity
            try:
                activity = MongoUserActivity(
                    user_id=str(current_user.id),
                    activity_type=ActivityType.VALIDATION_SESSION_UPDATED,
                    description=f"Updated validation session status to: {new_status}",
                    activity_metadata={
                        "session_id": session_id,
                        "old_status": session.status,
                        "new_status": new_status
                    }
                )
                await activity.insert()
            except Exception as e:
                logging.error(f"Failed to log activity: {e}")
        
        # Return updated session
        return ValidationSessionResponse(
            id=str(session.id),
            session_name=session.session_name,
            file_id=str(session.file_id) if session.file_id else None,
            template_id=str(session.template_id) if session.template_id else None,
            user_id=str(session.user_id),
            validation_type=session.validation_type,
            validation_rules=session.validation_rules or {},
            status=session.status,
            progress_percentage=session.progress_percentage,
            validation_results=session.validation_results,
            error_count=session.error_count,
            warning_count=session.warning_count,
            compliance_score=session.compliance_score,
            created_by=session.created_by,
            created_at=session.created_at,
            updated_at=session.updated_at,
            completed_at=session.completed_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while updating session status: {str(e)}"
        ) 