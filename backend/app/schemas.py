"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import ApplicationStatus, FundingStage, FileStatus, UserRole

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# First define UserProfile to avoid forward reference issues
class UserProfile(BaseModel):
    """User profile information (no sensitive data)"""
    id: int
    email: EmailStr
    full_name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Authentication Schemas
class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """User login response with tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)

class RegisterResponse(BaseModel):
    """User registration response"""
    message: str
    user: UserProfile

class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.ANALYST

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None

class User(UserBase):
    id: int
    profile_picture: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Industry Schemas
class IndustryBase(BaseModel):
    name: str
    description: Optional[str] = None

class Industry(IndustryBase):
    id: int
    
    class Config:
        from_attributes = True

# Founder Schemas
class FounderBase(BaseModel):
    name: str
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    years_experience: Optional[int] = None
    previous_companies: Optional[str] = None
    education: Optional[str] = None
    expertise_areas: Optional[str] = None

class FounderCreate(FounderBase):
    pass

class Founder(FounderBase):
    id: int
    startup_application_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# File Upload Schemas
class UploadedFileBase(BaseModel):
    filename: str
    original_filename: str
    file_type: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

class UploadedFile(UploadedFileBase):
    id: int
    startup_application_id: int
    file_path: Optional[str] = None
    status: FileStatus
    processing_progress: int = 0
    extraction_metadata: Optional[Dict[str, Any]] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Financial Metrics Schemas
class FinancialMetricBase(BaseModel):
    metric_name: str
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = None
    metric_period: Optional[str] = None
    data_source: Optional[str] = None

class FinancialMetricCreate(FinancialMetricBase):
    pass

class FinancialMetric(FinancialMetricBase):
    id: int
    startup_application_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Startup Application Schemas
class StartupApplicationBase(BaseModel):
    company_name: str
    website: Optional[str] = None
    contact_email: EmailStr
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    funding_stage: Optional[FundingStage] = None
    funding_amount_requested: Optional[float] = None
    current_arr: Optional[float] = None
    gross_margin: Optional[float] = None
    runway_months: Optional[int] = None

    # Add this validator to your schema
    @validator('funding_stage', pre=True)
    def format_funding_stage(cls, v):
        if isinstance(v, str):
            # Converts "Pre-Seed" to "pre_seed" and "series_d+" to "series_d_plus"
            v = v.lower().replace(' ', '_').replace('+', '_plus')
            return v
        return v

class StartupApplicationCreate(StartupApplicationBase):
    industry_id: Optional[int] = None

class StartupApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    industry_id: Optional[int] = None
    funding_stage: Optional[FundingStage] = None
    funding_amount_requested: Optional[float] = None
    current_arr: Optional[float] = None
    gross_margin: Optional[float] = None
    runway_months: Optional[int] = None
    status: Optional[ApplicationStatus] = None
    ai_score: Optional[float] = None
    manual_score: Optional[float] = None
    final_rating: Optional[str] = None
    assigned_analyst_id: Optional[int] = None
    processing_notes: Optional[str] = None

    # Add the same validator for funding_stage
    @validator('funding_stage', pre=True)
    def format_funding_stage(cls, v):
        if isinstance(v, str):
            # Converts "Pre-Seed" to "pre_seed" and "series_d+" to "series_d_plus"
            v = v.lower().replace(' ', '_').replace('-', '_').replace('+', '_plus')
            return v
        return v

class StartupApplication(StartupApplicationBase):
    id: int
    industry_id: Optional[int] = None
    status: ApplicationStatus
    ai_score: Optional[float] = None
    manual_score: Optional[float] = None
    final_rating: Optional[str] = None
    submitted_at: datetime
    assigned_at: Optional[datetime] = None
    assigned_analyst_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    processing_notes: Optional[str] = None
    bottleneck_stage: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    industry: Optional[Industry] = None
    assigned_analyst: Optional[User] = None
    founders: List[Founder] = []
    uploaded_files: List[UploadedFile] = []
    financial_metrics: List[FinancialMetric] = []
    
    class Config:
        from_attributes = True

# Investment Memo Schemas
class InvestmentMemoBase(BaseModel):
    executive_summary: Optional[str] = None
    investment_highlights: Optional[str] = None
    market_analysis: Optional[str] = None
    business_model_analysis: Optional[str] = None
    team_analysis: Optional[str] = None
    financial_analysis: Optional[str] = None
    risks_concerns: Optional[str] = None
    recommendation: Optional[str] = None
    recommended_investment: Optional[float] = None
    proposed_valuation: Optional[float] = None

class InvestmentMemoCreate(InvestmentMemoBase):
    startup_application_id: int

class InvestmentMemoUpdate(InvestmentMemoBase):
    is_draft: Optional[bool] = None
    partner_review_scheduled: Optional[bool] = None
    partner_review_date: Optional[datetime] = None

class InvestmentMemo(InvestmentMemoBase):
    id: int
    startup_application_id: int
    author_id: int
    is_draft: bool
    partner_review_scheduled: bool
    partner_review_date: Optional[datetime] = None
    approved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    author: Optional[User] = None
    startup_application: Optional[StartupApplication] = None
    
    class Config:
        from_attributes = True

# Dashboard and Analytics Schemas
class PipelineMetrics(BaseModel):
    total_applications: int
    applications_in_ai_processing: int
    completed_evaluations: int
    average_ai_score: float
    average_processing_time: float
    data_processing_conversion: float
    ai_analysis_conversion: float
    partner_review_conversion: float
    avg_days_data_processing: float
    avg_days_ai_analysis: float
    avg_days_manual_review: float
    calculated_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_applications: int
    ai_processing: int
    completed_analysis: int
    average_score: float
    recent_applications: List[StartupApplication]
    pipeline_metrics: PipelineMetrics

class DealPipelineStats(BaseModel):
    stages: Dict[str, int]  # status -> count
    conversion_rates: Dict[str, float]  # stage -> conversion %
    avg_days_per_stage: Dict[str, float]  # stage -> avg days
    bottlenecks: Dict[str, int]  # bottleneck -> count
    weekly_throughput: int

# Investment Weights Schema
class InvestmentWeights(BaseModel):
    id: Optional[int] = None
    market_size_weight: float = 25.0
    team_experience_weight: float = 30.0
    business_model_weight: float = 20.0
    traction_weight: float = 15.0
    financial_health_weight: float = 10.0
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Pagination and Filtering
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

class StartupFilters(BaseModel):
    status: Optional[ApplicationStatus] = None
    industry_id: Optional[int] = None
    funding_stage: Optional[FundingStage] = None
    assigned_analyst_id: Optional[int] = None
    min_ai_score: Optional[float] = None
    max_ai_score: Optional[float] = None
    search: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool

# Specific paginated responses
class PaginatedStartups(BaseModel):
    items: List[StartupApplication]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedMemos(BaseModel):
    items: List[InvestmentMemo]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool