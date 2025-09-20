"""
Configuration management for AIAlchemy backend.
Uses Pydantic Settings for environment variable management.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application Settings
    app_name: str = Field(default="AIAlchemy", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # Security
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "*.run.app"],
        env="ALLOWED_HOSTS"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Google Cloud Configuration
    google_cloud_project: str = Field(..., env="GOOGLE_CLOUD_PROJECT")
    google_application_credentials: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    
    # Vertex AI Configuration
    vertex_ai_project: str = Field(..., env="VERTEX_AI_PROJECT")
    vertex_ai_location: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")
    
    # Document AI Configuration
    document_ai_processor_id: Optional[str] = Field(
        default=None, env="DOCUMENT_AI_PROCESSOR_ID"
    )
    
    # Dialogflow Configuration
    dialogflow_agent_id: Optional[str] = Field(
        default=None, env="DIALOGFLOW_AGENT_ID"
    )
    
    # External API Keys
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    crunchbase_api_key: Optional[str] = Field(default=None, env="CRUNCHBASE_API_KEY")
    linkedin_api_key: Optional[str] = Field(default=None, env="LINKEDIN_API_KEY")
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    
    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # File Upload Configuration
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    allowed_file_types: List[str] = Field(
        default=["pdf", "ppt", "pptx", "mp4", "mp3", "wav"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # Storage Configuration
    bucket_app_storage: str = Field(..., env="BUCKET_APP_STORAGE")
    bucket_ml_models: Optional[str] = Field(default=None, env="BUCKET_ML_MODELS")
    bucket_documents: Optional[str] = Field(default=None, env="BUCKET_DOCUMENTS")
    
    # Feature Flags
    enable_ai_interviews: bool = Field(default=True, env="ENABLE_AI_INTERVIEWS")
    enable_real_time_benchmarking: bool = Field(
        default=True, env="ENABLE_REAL_TIME_BENCHMARKING"
    )
    enable_advanced_analytics: bool = Field(
        default=True, env="ENABLE_ADVANCED_ANALYTICS"
    )
    
    # Monitoring Configuration
    enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Celery Configuration (for background tasks)
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.environment == "staging"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic migrations)."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to avoid reading environment variables multiple times.
    """
    return Settings()