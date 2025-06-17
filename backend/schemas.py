from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
import re
from enum import Enum

# Enums
class ActivityType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    VALIDATION_START = "validation_start"
    VALIDATION_COMPLETE = "validation_complete"
    VALIDATION_SESSION_CREATED = "validation_session_created"
    TEMPLATE_CREATE = "template_create"
    TEMPLATE_UPDATE = "template_update"
    TEMPLATE_DELETE = "template_delete"
    REPORT_GENERATE = "report_generate"
    SETTINGS_UPDATE = "settings_update"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    last_login: Optional[datetime] = None
    login_count: int
    profile_picture: Optional[str] = None
    department: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    department: Optional[str] = None
    profile_picture: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v

# User Activity schemas
class UserActivityCreate(BaseModel):
    activity_type: ActivityType
    description: Optional[str] = None
    activity_metadata: Optional[Dict[str, Any]] = None
    resource_id: Optional[str] = None

class UserActivityResponse(UserActivityCreate):
    id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Reference File schemas
class ReferenceFileCreate(BaseModel):
    unique_key: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    file_id: str
    category: Optional[str] = None
    version: str = Field(default="1.0")
    reference_metadata: Optional[Dict[str, Any]] = None

class ReferenceFileResponse(ReferenceFileCreate):
    id: str
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# File upload schemas
class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    XLSX = "xlsx"
    XLS = "xls"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    TIF = "tif"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: FileType
    file_size: int
    upload_timestamp: datetime
    processing_status: ProcessingStatus
    message: str

class FileResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    file_extension: str
    content_type: Optional[str] = None
    description: Optional[str] = None
    category: str
    user_id: str
    uploaded_by: str
    upload_date: datetime
    is_processed: bool
    processing_status: str
    validation_report: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class FileProcessingUpdate(BaseModel):
    processing_status: ProcessingStatus
    progress_percentage: Optional[int] = None
    message: Optional[str] = None
    error_details: Optional[str] = None

class UploadedFileInfo(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int
    file_path: str
    upload_timestamp: datetime
    processing_status: ProcessingStatus
    progress_percentage: Optional[int] = None
    extracted_text: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    file_hash: Optional[str] = None
    download_count: int
    last_accessed: Optional[datetime] = None
    file_tags: Optional[List[str]] = None
    is_reference: bool
    user_id: str

    class Config:
        from_attributes = True

class FileListResponse(BaseModel):
    files: List[FileResponse]
    total_count: int
    page_size: int
    current_page: int

# Validation session schemas
class ValidationSessionBase(BaseModel):
    session_name: str = Field(..., min_length=1, max_length=200)

class ValidationSessionCreate(BaseModel):
    session_name: str = Field(..., min_length=1, max_length=200)
    file_id: Optional[str] = None  # Made optional for manual validation sessions
    template_id: Optional[str] = None
    validation_type: str = Field(default="standard")
    validation_rules: Optional[Dict[str, Any]] = None

class ValidationSessionResponse(BaseModel):
    id: str
    session_name: str
    file_id: Optional[str] = None  # Made optional for manual validation sessions
    template_id: Optional[str] = None
    user_id: str
    validation_type: str
    validation_rules: Optional[Dict[str, Any]] = None
    status: str
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    validation_results: Optional[Dict[str, Any]] = None
    error_count: Optional[int] = None
    warning_count: Optional[int] = None
    compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Template schemas
class ValidationRule(BaseModel):
    term_name: str
    expected_value: Optional[str] = None
    expected_range: Optional[str] = None
    validation_type: str  # exact_match, range_check, pattern_match, fuzzy_match
    required: bool = True
    tolerance: Optional[float] = Field(None, ge=0.0, le=1.0)

class MasterTemplateCreate(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    template_type: str = Field(default="standard")
    validation_rules: Optional[Dict[str, Any]] = None
    expected_columns: Optional[List[str]] = None
    required_columns: Optional[List[str]] = None
    data_types: Optional[Dict[str, str]] = None
    validation_constraints: Optional[Dict[str, Any]] = None
    is_active: bool = Field(default=True)

class MasterTemplateResponse(BaseModel):
    id: str
    template_name: str
    description: Optional[str] = None
    validation_rules: List[ValidationRule]
    created_by: str
    is_active: bool
    version: str
    usage_count: int
    last_used: Optional[datetime] = None
    category: Optional[str] = None
    template_tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TemplateResponse(BaseModel):
    id: str
    template_name: str
    description: Optional[str] = None
    template_type: str
    validation_rules: Optional[Dict[str, Any]] = None
    expected_columns: Optional[List[str]] = None
    required_columns: Optional[List[str]] = None
    data_types: Optional[Dict[str, str]] = None
    validation_constraints: Optional[Dict[str, Any]] = None
    is_active: bool
    usage_count: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Extracted Term schemas
class ExtractedTerm(BaseModel):
    id: Optional[str] = None
    session_id: str
    term_name: str
    extracted_value: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    location_in_text: Optional[str] = None
    extraction_method: str
    is_validated: bool = False
    term_category: Optional[str] = None
    data_type: Optional[str] = None

class ExtractedTermResponse(ExtractedTerm):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Validation Result schemas
class ValidationResult(BaseModel):
    id: Optional[str] = None
    session_id: str
    term_id: Optional[str] = None
    term_name: str
    expected_value: Optional[str] = None
    extracted_value: Optional[str] = None
    validation_status: str  # valid, invalid, missing, warning
    match_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_method: str
    notes: Optional[str] = None
    requires_review: bool = False

class ValidationResultResponse(ValidationResult):
    id: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Metrics schemas
class DashboardMetricsCreate(BaseModel):
    metric_name: str
    metric_value: float
    metric_type: str
    period: str
    date: datetime
    metrics_metadata: Optional[Dict[str, Any]] = None

class DashboardMetricsResponse(DashboardMetricsCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class SessionMetricsResponse(BaseModel):
    id: str
    session_id: str
    total_terms_extracted: int
    valid_terms_count: int
    invalid_terms_count: int
    missing_terms_count: int
    warning_terms_count: int
    overall_accuracy: Optional[float] = None
    processing_duration: Optional[float] = None
    extraction_accuracy: Optional[float] = None
    validation_accuracy: Optional[float] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FileMetricsResponse(BaseModel):
    id: str
    file_id: str
    processing_time: Optional[float] = None
    text_extraction_time: Optional[float] = None
    total_characters: Optional[int] = None
    total_words: Optional[int] = None
    total_pages: Optional[int] = None
    language_detected: Optional[str] = None
    quality_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Validation Summary schema
class ValidationSummary(BaseModel):
    session_id: str
    total_terms: int
    valid_terms: int
    invalid_terms: int
    missing_terms: int
    warning_terms: int
    overall_accuracy: float = Field(..., ge=0.0, le=1.0)
    compliance_status: str  # compliant, non_compliant, partial_compliant
    recommendations: List[str] = []

# Audit schemas
class SystemAuditResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Settings schemas
class NotificationSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    validation_complete: Optional[bool] = None
    validation_failed: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    system_updates: Optional[bool] = None

class NotificationSettingsResponse(BaseModel):
    id: str
    user_id: str
    email_notifications: bool
    validation_complete: bool
    validation_failed: bool
    weekly_summary: bool
    system_updates: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ApplicationSettingUpdate(BaseModel):
    setting_value: Dict[str, Any]
    description: Optional[str] = None

class ApplicationSettingResponse(BaseModel):
    id: str
    setting_key: str
    setting_value: Dict[str, Any]
    description: Optional[str] = None
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# Success response
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

# Analytics and Dashboard schemas
class DashboardStats(BaseModel):
    total_users: int
    total_files: int
    total_sessions: int
    total_templates: int
    active_sessions: int
    success_rate: float
    average_processing_time: float
    recent_activities: List[UserActivityResponse]

class ValidationReportRequest(BaseModel):
    session_id: str
    report_format: str = Field(default="detailed")  # summary, detailed, comparison
    include_recommendations: bool = True
    include_extracted_text: bool = False

class NLPAnalysisResult(BaseModel):
    file_id: str
    extracted_entities: List[dict] = []
    key_phrases: List[str] = []
    sentiment_analysis: Optional[dict] = None
    language_detected: Optional[str] = None
    document_classification: Optional[str] = None
    processing_time: float

# Enhanced Validation Interface Schemas

class TradeRecordCreate(BaseModel):
    trade_id: str = Field(..., min_length=1, max_length=50)
    counterparty: str = Field(..., min_length=1, max_length=200)
    notional_amount: float = Field(..., gt=0)
    settlement_date: datetime
    interest_rate: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    payment_terms: str = Field(..., min_length=1, max_length=100)
    legal_entity: str = Field(..., min_length=1, max_length=200)
    trade_type: Optional[str] = Field(default="Standard", max_length=50)
    maturity_date: Optional[datetime] = None
    reference_rate: Optional[str] = Field(None, max_length=50)

class TradeRecordResponse(TradeRecordCreate):
    id: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TermSheetDataResponse(BaseModel):
    id: str
    session_id: str
    trade_id: Optional[str] = None
    counterparty: Optional[str] = None
    notional_amount: Optional[str] = None
    settlement_date: Optional[str] = None
    interest_rate: Optional[str] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    legal_entity: Optional[str] = None
    extraction_confidence: Dict[str, float] = {}
    extraction_source: Dict[str, str] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ValidationDiscrepancyResponse(BaseModel):
    id: str
    session_id: str
    discrepancy_type: str
    field_name: str
    term_sheet_value: Optional[str] = None
    trade_record_value: Optional[str] = None
    confidence_score: float
    impact_level: str
    description: str
    recommendation: Optional[str] = None
    status: str
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ValidationDecisionCreate(BaseModel):
    decision: str = Field(..., pattern="^(approve|reject|manual_review)$")
    decision_reason: Optional[str] = None
    
class ValidationDecisionResponse(BaseModel):
    id: str
    session_id: str
    decision: str
    decision_reason: Optional[str] = None
    ai_risk_score: float
    mifid_status: str
    fca_status: str
    sec_status: str
    total_discrepancies: int
    critical_issues: int
    minor_issues: int
    decided_by: str
    decided_at: datetime

    class Config:
        from_attributes = True

class ValidationInterfaceData(BaseModel):
    """Complete validation interface data"""
    session: ValidationSessionResponse
    term_sheet_data: Optional[TermSheetDataResponse] = None
    trade_record: Optional[TradeRecordResponse] = None
    discrepancies: List[ValidationDiscrepancyResponse] = []
    validation_decision: Optional[ValidationDecisionResponse] = None
    validation_analysis: Optional[Dict[str, Any]] = Field(default_factory=dict)
    compliance_status: Optional[Dict[str, str]] = Field(default_factory=dict)

class AIAnalysisResult(BaseModel):
    """AI Analysis results for validation interface"""
    session_id: str
    detected_discrepancies: int
    critical_issues: List[str] = []
    minor_issues: List[str] = []
    warnings: List[str] = []
    ai_risk_score: float = Field(..., ge=0, le=100)
    mifid_assessment: str
    fca_assessment: str
    sec_assessment: str
    recommendations: List[str] = []
    processing_time: float

# Request schemas for validation interface
class ValidationSessionStartRequest(BaseModel):
    file_id: Optional[str] = None  # Made optional for manual validation sessions
    trade_id: Optional[str] = None  # Optional trade ID to match against
    
class ValidationInterfaceRequest(BaseModel):
    session_id: str 