from beanie import Document, Indexed, before_event, Insert, Update
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

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

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    WARNING = "warning"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    PARTIAL_COMPLIANT = "partial_compliant"
    NON_COMPLIANT = "non_compliant"

# MongoDB Documents

class User(Document):
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    last_login: Optional[datetime] = None
    login_count: int = 0
    profile_picture: Optional[str] = None
    department: Optional[str] = None
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "is_active",
            "role"
        ]

class UserActivity(Document):
    user_id: str
    activity_type: ActivityType
    description: Optional[str] = None
    activity_metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    resource_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_activities"
        indexes = [
            "user_id",
            "activity_type",
            "timestamp"
        ]

class UploadedFile(Document):
    file_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    file_path: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    progress_percentage: int = 0
    extracted_text: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    file_hash: Optional[str] = None
    download_count: int = 0
    last_accessed: Optional[datetime] = None
    file_tags: Optional[List[str]] = None
    is_reference: bool = False
    user_id: str
    
    class Settings:
        name = "uploaded_files"
        indexes = [
            "file_id",
            "user_id",
            "processing_status",
            "upload_timestamp"
        ]

class ReferenceFile(Document):
    unique_key: Indexed(str, unique=True)
    name: str
    description: Optional[str] = None
    file_id: str
    category: Optional[str] = None
    version: str = "1.0"
    is_active: bool = True
    reference_metadata: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "reference_files"
        indexes = [
            "unique_key",
            "file_id",
            "created_by",
            "category"
        ]

class MasterTemplate(Document):
    template_name: str
    description: Optional[str] = None
    validation_rules: List[Dict[str, Any]]
    created_by: str
    is_active: bool = True
    version: str = "1.0"
    usage_count: int = 0
    last_used: Optional[datetime] = None
    category: Optional[str] = None
    template_tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "master_templates"
        indexes = [
            "created_by",
            "is_active",
            "category",
            "usage_count"
        ]

class ValidationSession(Document):
    session_name: str
    file_id: Optional[str] = None  # Made optional for manual validation sessions
    template_id: Optional[str] = None
    validation_type: str = "standard"
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress_percentage: int = 0
    
    # Additional fields needed for validation responses
    validation_results: Optional[Dict[str, Any]] = None
    error_count: Optional[int] = 0
    warning_count: Optional[int] = 0
    compliance_score: Optional[float] = None
    created_by: str = "system"
    updated_at: Optional[datetime] = None
    
    # Existing fields
    total_terms: Optional[int] = None
    validated_terms: Optional[int] = None
    accuracy_score: Optional[float] = None
    compliance_status: Optional[ComplianceStatus] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    session_configuration: Optional[Dict[str, Any]] = None
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    
    @property
    def validation_rules(self) -> Optional[Dict[str, Any]]:
        """Get validation rules from session configuration"""
        return self.session_configuration
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "validation_sessions"
        indexes = [
            "user_id",
            "file_id",
            "status",
            "created_at"
        ]

class ExtractedTerm(Document):
    session_id: str
    term_name: str
    extracted_value: Optional[str] = None
    confidence_score: Optional[float] = None
    location_in_text: Optional[str] = None
    extraction_method: str
    is_validated: bool = False
    term_category: Optional[str] = None
    data_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "extracted_terms"
        indexes = [
            "session_id",
            "term_name",
            "is_validated"
        ]

class ValidationResult(Document):
    session_id: str
    term_id: Optional[str] = None
    term_name: str
    expected_value: Optional[str] = None
    extracted_value: Optional[str] = None
    validation_status: ValidationStatus
    match_score: Optional[float] = None
    validation_method: str
    notes: Optional[str] = None
    requires_review: bool = False
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "validation_results"
        indexes = [
            "session_id",
            "validation_status",
            "requires_review"
        ]

class DashboardMetrics(Document):
    metric_name: Indexed(str)
    metric_value: float
    metric_type: str
    period: str
    date: Indexed(datetime)
    metrics_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "dashboard_metrics"
        indexes = [
            "metric_name",
            "date",
            "period"
        ]

class SessionMetrics(Document):
    session_id: str
    total_terms_extracted: int = 0
    valid_terms_count: int = 0
    invalid_terms_count: int = 0
    missing_terms_count: int = 0
    warning_terms_count: int = 0
    overall_accuracy: Optional[float] = None
    processing_duration: Optional[float] = None
    extraction_accuracy: Optional[float] = None
    validation_accuracy: Optional[float] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "session_metrics"
        indexes = [
            "session_id"
        ]

class FileMetrics(Document):
    file_id: str
    processing_time: Optional[float] = None
    text_extraction_time: Optional[float] = None
    total_characters: Optional[int] = None
    total_words: Optional[int] = None
    total_pages: Optional[int] = None
    language_detected: Optional[str] = None
    quality_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "file_metrics"
        indexes = [
            "file_id"
        ]

class SystemAudit(Document):
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "system_audit"
        indexes = [
            "user_id",
            "action",
            "resource_type",
            "timestamp"
        ]

class NotificationSettings(Document):
    user_id: Indexed(str, unique=True)
    email_notifications: bool = True
    validation_complete: bool = True
    validation_failed: bool = True
    weekly_summary: bool = True
    system_updates: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "notification_settings"
        indexes = [
            "user_id"
        ]

class ApplicationSettings(Document):
    setting_key: Indexed(str, unique=True)
    setting_value: Dict[str, Any]
    description: Optional[str] = None
    is_system: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "application_settings"
        indexes = [
            "setting_key",
            "is_system"
        ]

class TradeRecord(Document):
    """Internal trade record for validation comparison"""
    trade_id: Indexed(str, unique=True)
    counterparty: str
    notional_amount: float
    settlement_date: datetime
    interest_rate: float
    currency: str = "USD"
    payment_terms: str
    legal_entity: str
    trade_type: Optional[str] = "Standard"
    maturity_date: Optional[datetime] = None
    reference_rate: Optional[str] = None
    status: str = "active"
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "trade_records"
        indexes = [
            "trade_id",
            "counterparty",  
            "created_by",
            "status"
        ]

class TermSheetData(Document):
    """Extracted term sheet data for validation"""
    session_id: str  # Links to ValidationSession
    trade_id: Optional[str] = None
    counterparty: Optional[str] = None
    notional_amount: Optional[str] = None  # Store as string initially
    settlement_date: Optional[str] = None
    interest_rate: Optional[str] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    legal_entity: Optional[str] = None
    
    # Extraction metadata
    extraction_confidence: Dict[str, float] = {}  # Field confidence scores
    extraction_source: Dict[str, str] = {}  # Source location in document
    raw_extracted_data: Optional[Dict[str, Any]] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @before_event(Update)
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "term_sheet_data"
        indexes = [
            "session_id",
            "trade_id"
        ]

class ValidationDiscrepancy(Document):
    """AI-detected discrepancies between term sheet and trade record"""
    session_id: str
    discrepancy_type: str  # "critical", "minor", "warning"
    field_name: str
    term_sheet_value: Optional[str] = None
    trade_record_value: Optional[str] = None
    confidence_score: float
    impact_level: str  # "high", "medium", "low"
    description: str
    recommendation: Optional[str] = None
    status: str = "pending"  # "pending", "resolved", "ignored"
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "validation_discrepancies"
        indexes = [
            "session_id",
            "discrepancy_type",
            "status"
        ]

class ValidationDecision(Document):
    """Final validation decision and actions"""
    session_id: str
    decision: str  # "approve", "reject", "manual_review"
    decision_reason: Optional[str] = None
    ai_risk_score: float
    mifid_status: str  # "warning", "compliant"
    fca_status: str   # "compliant", "non_compliant"
    sec_status: str   # "compliant", "non_compliant"
    
    # Decision metadata
    total_discrepancies: int = 0
    critical_issues: int = 0
    minor_issues: int = 0
    
    decided_by: str
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "validation_decisions"
        indexes = [
            "session_id",
            "decision",
            "decided_by"
        ] 