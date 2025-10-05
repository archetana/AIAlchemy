"""
SQLAlchemy Database Models for AIAlchemy Platform
Based on mockup analysis: Dashboard, Deal Pipeline, Upload, Investment Memo, Settings
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, Enum, JSON, LargeBinary
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime
from typing import Optional, List

# Enums for status fields
class ApplicationStatus(str, enum.Enum):
    NEW = "new"
    DATA_PROCESSING = "data_processing" 
    AI_ANALYSIS = "ai_analysis"
    MANUAL_REVIEW = "manual_review"
    PARTNER_REVIEW = "partner_review"
    COMPLETED = "completed"
    REJECTED = "rejected"

class FundingStage(str, enum.Enum):
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    GROWTH = "growth"

class FileStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PARTNER = "partner"
    ANALYST = "analyst"
    VIEWER = "viewer"

# Core Models

class User(Base):
    """User model for account management and settings"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    title = Column(String(255))
    phone = Column(String(50))
    profile_picture = Column(String(500))  # URL or path
    role = Column(Enum(UserRole), default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    startup_applications = relationship("StartupApplication", back_populates="assigned_analyst")
    investment_memos = relationship("InvestmentMemo", back_populates="author")

class Industry(Base):
    """Industry categories for startup classification"""
    __tablename__ = "industries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    startups = relationship("StartupApplication", back_populates="industry")

class StartupApplication(Base):
    """Main startup application model - central to the platform"""
    __tablename__ = "startup_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    website = Column(String(500))
    contact_email = Column(String(255), nullable=False)
    contact_name = Column(String(255))
    contact_phone = Column(String(50))
    
    # Business Info
    industry_id = Column(Integer, ForeignKey("industries.id"))
    funding_stage = Column(Enum(FundingStage))
    funding_amount_requested = Column(Float)
    current_arr = Column(Float)  # Annual Recurring Revenue
    gross_margin = Column(Float)
    runway_months = Column(Integer)
    
    # Status and Processing
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.NEW, index=True)
    ai_score = Column(Float)  # AI evaluation score (0-100)
    manual_score = Column(Float)  # Manual evaluation score (0-100)
    final_rating = Column(String(50))  # e.g., "Strong Invest", "Pass", etc.
    
    # Timestamps and Assignment
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True))
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime(timezone=True))
    
    # Processing metadata
    processing_notes = Column(Text)
    bottleneck_stage = Column(String(100))  # Track where applications get stuck
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    industry = relationship("Industry", back_populates="startups")
    assigned_analyst = relationship("User", back_populates="startup_applications")
    uploaded_files = relationship("UploadedFile", back_populates="startup_application")
    founders = relationship("Founder", back_populates="startup_application")
    financial_metrics = relationship("FinancialMetric", back_populates="startup_application")
    investment_memo = relationship("InvestmentMemo", back_populates="startup_application", uselist=False)
    evaluation_history = relationship("EvaluationHistory", back_populates="startup_application")

class Founder(Base):
    """Founder profiles for founder analysis section"""
    __tablename__ = "founders"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    linkedin_url = Column(String(500))
    years_experience = Column(Integer)
    previous_companies = Column(Text)  # JSON string or comma-separated
    education = Column(Text)
    expertise_areas = Column(Text)  # JSON string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    startup_application = relationship("StartupApplication", back_populates="founders")

class UploadedFile(Base):
    """File management for pitch decks and documents"""
    __tablename__ = "uploaded_files"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID from file storage service
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    
    # File metadata
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)  # Generated filename with UUID
    file_type = Column(String(100))  # "pitch_deck", "financial_docs", "team_info", etc.
    content_type = Column(String(200), nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64))  # SHA-256 hash for deduplication
    
    # Storage information
    file_path = Column(String(1000), nullable=False)  # Full storage path (local or GCS)
    relative_path = Column(String(500))  # Relative path for organization
    storage_backend = Column(String(50), default='local')  # 'local' or 'gcs'
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_progress = Column(Integer, default=0)  # 0-100%
    
    # Metadata and security
    description = Column(Text)  # User-provided description
    metadata_json = Column(JSON)  # Extracted data, scan results, etc.
    is_safe = Column(Boolean, default=True)  # Virus scan result
    
    # Timestamps
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Relationships
    startup_application = relationship("StartupApplication", back_populates="uploaded_files")

class FinancialMetric(Base):
    """Financial metrics extracted from documents or manually entered"""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    
    metric_name = Column(String(255), nullable=False)  # "ARR", "Gross Margin", etc.
    metric_value = Column(Float)
    metric_unit = Column(String(50))  # "$", "%", "months", etc.
    metric_period = Column(String(100))  # "2024", "Q3 2024", etc.
    data_source = Column(String(100))  # "pitch_deck", "financial_model", "manual"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    startup_application = relationship("StartupApplication", back_populates="financial_metrics")

class InvestmentMemo(Base):
    """Investment memo with executive summary and recommendations"""
    __tablename__ = "investment_memos"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Memo Sections
    executive_summary = Column(Text)
    investment_highlights = Column(Text)
    market_analysis = Column(Text)
    business_model_analysis = Column(Text)
    team_analysis = Column(Text)
    financial_analysis = Column(Text)
    risks_concerns = Column(Text)
    
    # Recommendation
    recommendation = Column(String(100))  # "Strong Invest", "Invest", "Pass", etc.
    recommended_investment = Column(Float)
    proposed_valuation = Column(Float)
    
    # Review Status
    is_draft = Column(Boolean, default=True)
    partner_review_scheduled = Column(Boolean, default=False)
    partner_review_date = Column(DateTime(timezone=True))
    approved = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    startup_application = relationship("StartupApplication", back_populates="investment_memo")
    author = relationship("User", back_populates="investment_memos")

class EvaluationHistory(Base):
    """Track evaluation progress and status changes"""
    __tablename__ = "evaluation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    
    previous_status = Column(Enum(ApplicationStatus))
    new_status = Column(Enum(ApplicationStatus), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    time_in_previous_stage = Column(Integer)  # Minutes spent in previous stage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    startup_application = relationship("StartupApplication", back_populates="evaluation_history")

# Analytics and Dashboard Models

class PipelineMetrics(Base):
    """Pre-calculated metrics for dashboard performance"""
    __tablename__ = "pipeline_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metrics
    total_applications = Column(Integer, default=0)
    applications_in_ai_processing = Column(Integer, default=0)
    completed_evaluations = Column(Integer, default=0)
    average_ai_score = Column(Float, default=0.0)
    average_processing_time = Column(Float, default=0.0)  # Days
    
    # Conversion rates
    data_processing_conversion = Column(Float, default=0.0)
    ai_analysis_conversion = Column(Float, default=0.0)
    partner_review_conversion = Column(Float, default=0.0)
    
    # Bottleneck analysis
    avg_days_data_processing = Column(Float, default=0.0)
    avg_days_ai_analysis = Column(Float, default=0.0)
    avg_days_manual_review = Column(Float, default=0.0)
    
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

class InvestmentWeights(Base):
    """Investment criteria weights for AI scoring"""
    __tablename__ = "investment_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Weights (should sum to 100)
    market_size_weight = Column(Float, default=25.0)
    team_experience_weight = Column(Float, default=30.0)
    business_model_weight = Column(Float, default=20.0)
    traction_weight = Column(Float, default=15.0)
    financial_health_weight = Column(Float, default=10.0)
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Document Processing and AI Pipeline Models

class DocumentProcessingStatus(str, enum.Enum):
    """Status for document processing pipeline"""
    PENDING = "pending"
    VALIDATING = "validating"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(str, enum.Enum):
    """Pipeline processing stages"""
    INITIALIZATION = "initialization"
    DOCUMENT_VALIDATION = "document_validation" 
    DOCUMENT_PROCESSING = "document_processing"
    DATA_EXTRACTION = "data_extraction"
    MEMO_GENERATION = "memo_generation"
    QUALITY_ASSURANCE = "quality_assurance"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingPipeline(Base):
    """Document processing pipeline tracking"""
    __tablename__ = "processing_pipelines"
    
    id = Column(String(50), primary_key=True, index=True)  # Custom pipeline ID
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    
    # Pipeline status and progress
    status = Column(Enum(DocumentProcessingStatus), default=DocumentProcessingStatus.PENDING, index=True)
    current_stage = Column(Enum(PipelineStage), default=PipelineStage.INITIALIZATION)
    progress_percentage = Column(Float, default=0.0)
    
    # Stage completion tracking
    stages_completed = Column(JSON)  # List of completed stages
    stages_failed = Column(JSON)     # List of failed stages
    
    # Timing information
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    total_duration_ms = Column(Integer)
    
    # Configuration and metadata
    processing_config = Column(JSON)  # Pipeline configuration
    input_files = Column(JSON)        # List of input file IDs
    
    # Error tracking
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    startup_application = relationship("StartupApplication")
    stage_results = relationship("PipelineStageResult", back_populates="pipeline")
    document_extractions = relationship("DocumentExtraction", back_populates="pipeline")


class PipelineStageResult(Base):
    """Results of individual pipeline stages"""
    __tablename__ = "pipeline_stage_results"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(String(50), ForeignKey("processing_pipelines.id"), nullable=False)
    
    # Stage information
    stage = Column(Enum(PipelineStage), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed, skipped
    
    # Timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)
    
    # Results and metadata
    result_data = Column(JSON)        # Stage output data
    stage_metadata = Column(JSON)     # Stage-specific metadata
    
    # Error tracking
    errors = Column(JSON)             # List of errors
    warnings = Column(JSON)           # List of warnings
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pipeline = relationship("ProcessingPipeline", back_populates="stage_results")


class DocumentExtraction(Base):
    """Document AI extraction results"""
    __tablename__ = "document_extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(String(50), ForeignKey("processing_pipelines.id"), nullable=False)
    file_id = Column(String(36), ForeignKey("uploaded_files.id"), nullable=False)
    
    # Extraction metadata
    extraction_method = Column(String(100))  # 'document_ai', 'fallback', etc.
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    
    # Extracted content
    raw_text = Column(Text)
    structured_data = Column(JSON)    # Structured extraction results
    
    # Business-specific extractions
    company_name = Column(String(255))
    industry = Column(String(255))
    problem_statement = Column(Text)
    solution_description = Column(Text)
    
    # Financial data extractions
    revenue_current = Column(Float)
    revenue_projected = Column(Float)
    funding_amount = Column(Float)
    funding_stage = Column(String(100))
    burn_rate = Column(Float)
    runway_months = Column(Integer)
    valuation = Column(Float)
    
    # Team data extractions
    founders = Column(JSON)           # List of founder names
    team_size = Column(Integer)
    key_roles = Column(JSON)          # List of key roles
    advisors = Column(JSON)           # List of advisors
    
    # Document metadata
    page_count = Column(Integer)
    language = Column(String(10))
    file_format = Column(String(50))
    
    # Quality and validation
    extraction_quality = Column(String(50))  # 'high', 'medium', 'low'
    validation_errors = Column(JSON)
    validation_warnings = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pipeline = relationship("ProcessingPipeline", back_populates="document_extractions")
    uploaded_file = relationship("UploadedFile")


class GeneratedMemo(Base):
    """AI-generated investment memos"""
    __tablename__ = "generated_memos"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_application_id = Column(Integer, ForeignKey("startup_applications.id"), nullable=False)
    pipeline_id = Column(String(50), ForeignKey("processing_pipelines.id"))
    
    # Generation metadata
    generation_method = Column(String(100))    # 'gemini_pro', 'fallback', etc.
    generation_model = Column(String(100))     # Model version used
    generation_time_ms = Column(Integer)
    total_words = Column(Integer)
    
    # Memo sections (comprehensive structure)
    executive_summary = Column(Text)
    investment_thesis = Column(Text)
    company_overview = Column(Text)
    market_analysis = Column(Text)
    business_model = Column(Text)
    team_assessment = Column(Text)
    financial_analysis = Column(Text)
    risk_assessment = Column(Text)
    competitive_landscape = Column(Text)
    recommendation = Column(Text)
    
    # AI Scoring and Analysis
    overall_score = Column(Float)              # 0-100 scale
    recommendation_type = Column(String(50))   # 'strong_buy', 'buy', 'hold', 'pass', 'strong_pass'
    risk_level = Column(String(50))            # 'low', 'medium_low', 'medium', 'medium_high', 'high'
    success_probability = Column(Float)         # 0-1 scale
    
    # Structured insights
    key_strengths = Column(JSON)               # List of key strengths
    key_concerns = Column(JSON)                # List of key concerns
    
    # Quality and validation
    confidence_score = Column(Float)
    quality_score = Column(Float)
    requires_review = Column(Boolean, default=False)
    
    # Memo configuration
    sections_generated = Column(JSON)          # List of sections included
    custom_instructions = Column(Text)         # Custom generation instructions
    memo_template = Column(String(100))        # Template used
    
    # Status and workflow
    is_draft = Column(Boolean, default=True)
    reviewed_by_human = Column(Boolean, default=False)
    approved_for_use = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    startup_application = relationship("StartupApplication")
    pipeline = relationship("ProcessingPipeline")


class ProcessingAgent(Base):
    """Agent performance and configuration tracking"""
    __tablename__ = "processing_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Agent identification
    agent_name = Column(String(100), nullable=False, index=True)
    agent_version = Column(String(50))
    agent_type = Column(String(100))           # 'document_ai', 'memo_generator', etc.
    
    # Configuration
    agent_config = Column(JSON)                # Agent configuration
    
    # Performance metrics
    total_processed = Column(Integer, default=0)
    total_successful = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    average_processing_time_ms = Column(Integer, default=0)
    
    # Quality metrics
    average_confidence_score = Column(Float, default=0.0)
    average_quality_score = Column(Float, default=0.0)
    
    # Status and health
    is_active = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True))
    health_status = Column(String(50))         # 'healthy', 'degraded', 'unhealthy'
    
    # Error tracking
    last_error = Column(Text)
    error_count_24h = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FileValidationLog(Base):
    """File validation and security scan logs"""
    __tablename__ = "file_validation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(36), ForeignKey("uploaded_files.id"), nullable=False)
    
    # Validation results
    validation_passed = Column(Boolean, nullable=False)
    file_size_bytes = Column(Integer)
    detected_mime_type = Column(String(200))
    file_hash_sha256 = Column(String(64))
    
    # Security scan results
    virus_scan_performed = Column(Boolean, default=False)
    virus_scan_result = Column(String(100))    # 'clean', 'infected', 'scan_failed'
    virus_scanner_version = Column(String(100))
    
    # Validation details
    validation_errors = Column(JSON)           # List of validation errors
    validation_warnings = Column(JSON)         # List of validation warnings
    
    # File content analysis
    content_type_verified = Column(Boolean, default=False)
    content_analysis_results = Column(JSON)
    
    # Processing metadata
    validation_time_ms = Column(Integer)
    validator_version = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    uploaded_file = relationship("UploadedFile")


class SystemConfiguration(Base):
    """System-wide configuration for AI processing"""
    __tablename__ = "system_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configuration identification
    config_key = Column(String(200), unique=True, nullable=False, index=True)
    config_category = Column(String(100), index=True)  # 'document_ai', 'gemini', 'pipeline', etc.
    
    # Configuration data
    config_value = Column(JSON)                # Configuration value (can be any type)
    config_description = Column(Text)
    
    # Versioning and management
    is_active = Column(Boolean, default=True)
    version = Column(String(50))
    
    # Access control
    is_sensitive = Column(Boolean, default=False)  # For API keys, credentials, etc.
    requires_restart = Column(Boolean, default=False)  # Whether changing this requires service restart
    
    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"))
    last_modified_by_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    last_modified_by = relationship("User", foreign_keys=[last_modified_by_id])
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Indexes for performance optimization
from sqlalchemy import Index

# Create composite indexes for common queries
Index('idx_startup_status_created', StartupApplication.status, StartupApplication.created_at)
Index('idx_startup_industry_status', StartupApplication.industry_id, StartupApplication.status)
Index('idx_startup_analyst_status', StartupApplication.assigned_analyst_id, StartupApplication.status)
Index('idx_files_startup_type', UploadedFile.startup_application_id, UploadedFile.file_type)
Index('idx_evaluation_startup_created', EvaluationHistory.startup_application_id, EvaluationHistory.created_at)