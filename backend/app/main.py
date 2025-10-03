"""
AIAlchemy FastAPI Backend
AI-powered startup evaluation platform with comprehensive API endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import routers
from app.routers import dashboard, startups, pipeline, memos, uploads, settings
from app.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting AIAlchemy API server...")
    
    # Initialize database
    try:
        from app.init_db_fixed import init_database
        print("🔧 Initializing database tables and data...")
        db_success = await init_database()
        if db_success:
            print("✅ Database initialized successfully")
        else:
            print("⚠️  Database initialization had issues, but continuing...")
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
        import traceback
        traceback.print_exc()
    
    print("📊 AIAlchemy API ready")
    yield
    # Shutdown
    print("🔒 Shutting down AIAlchemy API server...")

# Create FastAPI app
app = FastAPI(
    title="AIAlchemy API",
    description="AI-powered startup evaluation platform with comprehensive REST API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(dashboard.router)
app.include_router(startups.router)
app.include_router(pipeline.router)
app.include_router(memos.router)
app.include_router(uploads.router)
app.include_router(settings.router)

@app.get("/")
async def root():
    """Root endpoint with API overview"""
    return {
        "service": "AIAlchemy API",
        "status": "running", 
        "version": "1.0.0",
        "message": "AI-powered startup evaluation platform",
        "documentation": "/docs",
        "api_endpoints": {
            "dashboard": "/api/dashboard/stats",
            "startups": "/api/startups/",
            "pipeline": "/api/pipeline/stats", 
            "memos": "/api/memos/",
            "uploads": "/api/uploads/",
            "settings": "/api/settings/"
        },
        "features": [
            "Startup application management",
            "AI-powered evaluation pipeline",
            "Investment memo generation",
            "File upload and processing",
            "Comprehensive analytics dashboard",
            "User account management"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    from app.database import async_session_local
    from sqlalchemy import text
    
    db_status = "connected"
    tables_exist = False
    
    try:
        async with async_session_local() as session:
            # Check if startup_applications table exists
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='startup_applications'")
            )
            tables_exist = result.fetchone() is not None
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if tables_exist else "degraded",
        "service": "aialchemy-backend", 
        "database": db_status,
        "tables_initialized": tables_exist,
        "timestamp": "2025-01-20T16:00:00Z"
    }

@app.get("/api/status")
async def api_status():
    """Detailed API status endpoint"""
    return {
        "api": "operational",
        "version": "1.0.0",
        "database_type": "SQLite",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "available_endpoints": {
            "dashboard": [
                "GET /api/dashboard/stats",
                "GET /api/dashboard/overview"
            ],
            "startups": [
                "GET /api/startups/",
                "GET /api/startups/{id}",
                "POST /api/startups/",
                "PUT /api/startups/{id}"
            ],
            "pipeline": [
                "GET /api/pipeline/stats",
                "GET /api/pipeline/stages",
                "PUT /api/pipeline/applications/{id}/status"
            ],
            "memos": [
                "GET /api/memos/startup/{id}",
                "POST /api/memos/",
                "PUT /api/memos/{id}"
            ],
            "uploads": [
                "POST /api/uploads/startup/{id}/files",
                "GET /api/uploads/startup/{id}/files",
                "GET /api/uploads/files/{id}"
            ],
            "settings": [
                "GET /api/settings/users/me",
                "PUT /api/settings/users/me",
                "GET /api/settings/investment-weights"
            ]
        }
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)