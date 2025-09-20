"""
FastAPI application entry point for AIAlchemy
AI-powered startup evaluation platform
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import get_settings
from app.core.database import database_manager
from app.core.exceptions import AIAlchemyException
from app.api.auth import router as auth_router
from app.api.evaluations import router as evaluations_router
from app.api.pipeline import router as pipeline_router
from app.api.analytics import router as analytics_router
from app.api.interviews import router as interviews_router
from app.api.settings import router as settings_router

# Configure structured logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager for startup and shutdown events.
    """
    settings = get_settings()
    logger.info("Starting AIAlchemy backend", environment=settings.environment)
    
    try:
        # Initialize database connection
        await database_manager.connect()
        logger.info("Database connection established")
        
        # Initialize other services (Redis, Google Cloud services, etc.)
        # TODO: Add service initialization here
        
        yield
        
    finally:
        # Cleanup on shutdown
        await database_manager.disconnect()
        logger.info("AIAlchemy backend shutdown complete")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="AIAlchemy API",
        description="AI-powered startup evaluation platform",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan,
    )
    
    # Security Middleware
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Exception Handler
    @app.exception_handler(AIAlchemyException)
    async def aialchemy_exception_handler(request: Request, exc: AIAlchemyException):
        """Custom exception handler for AIAlchemy exceptions."""
        logger.error(
            "AIAlchemy exception",
            error=str(exc),
            status_code=exc.status_code,
            path=request.url.path
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "detail": exc.detail}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """General exception handler for unexpected errors."""
        logger.exception(
            "Unhandled exception",
            error=str(exc),
            path=request.url.path
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred"
            }
        )
    
    # Health Check Endpoints
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for load balancers."""
        return {"status": "healthy", "service": "aialchemy-backend"}
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "AIAlchemy API",
            "version": "1.0.0",
            "environment": settings.environment,
            "docs": "/docs" if settings.environment != "production" else "disabled"
        }
    
    # Include API Routers
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(evaluations_router, prefix="/api/v1/evaluations", tags=["Evaluations"])
    app.include_router(pipeline_router, prefix="/api/v1/pipeline", tags=["Pipeline"])
    app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
    app.include_router(interviews_router, prefix="/api/v1/interviews", tags=["Interviews"])
    app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])
    
    return app


# Create the FastAPI app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )