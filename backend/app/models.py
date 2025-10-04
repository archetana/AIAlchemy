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
    full_name = Column(String(255), nullable=False)
    title = Column(String(255))
    phone = Column(String(50))
    profile_picture = Column(String(500))  # URL or path
    role = Column(Enum(UserRole), default=UserRole.ANALYST)
    is_active = Column(Boolean, default=True)
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

# Indexes for performance optimization
from sqlalchemy import Index

# Create composite indexes for common queries
Index('idx_startup_status_created', StartupApplication.status, StartupApplication.created_at)
Index('idx_startup_industry_status', StartupApplication.industry_id, StartupApplication.status)
Index('idx_startup_analyst_status', StartupApplication.assigned_analyst_id, StartupApplication.status)
Index('idx_files_startup_type', UploadedFile.startup_application_id, UploadedFile.file_type)
Index('idx_evaluation_startup_created', EvaluationHistory.startup_application_id, EvaluationHistory.created_at)