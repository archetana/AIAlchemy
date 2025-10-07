"""
AIAlchemy FastAPI Backend
AI-powered startup evaluation platform with comprehensive API endpoints
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import routers
from app.routers import dashboard, startups, pipeline, memos, uploads, settings, auth, document_processing
from app.api.v1 import vector_documents, ai_models
from app.core.database import database_manager
from app.auth.auth_middleware import AuthenticationMiddleware, SecurityHeadersMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting AIAlchemy API server...")
    
    # Initialize database connection
    try:
        print("🔧 Connecting to database...")
        await database_manager.connect()
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        import traceback
        traceback.print_exc()
    
    # Run comprehensive startup checks
    try:
        from app.startup_checks import run_startup_checks, force_supabase_mode
        
        print("🔍 Running startup validation checks...")
        
        # Run all checks
        startup_summary = await run_startup_checks()
        
        # Print detailed results
        print(f"📊 Startup Check Results:")
        print(f"   Overall Status: {startup_summary['overall_status']}")
        print(f"   Checks Passed: {startup_summary['checks_passed']}/{startup_summary['total_checks']}")
        
        if startup_summary['failed_checks']:
            print(f"   ❌ Failed Checks:")
            for check in startup_summary['failed_checks']:
                print(f"      - {check}")
        
        if startup_summary['warnings']:
            print(f"   ⚠️ Warnings:")
            for warning in startup_summary['warnings']:
                print(f"      - {warning}")
        
        # Force Supabase mode in production if needed
        from app.core.config import get_settings
        settings = get_settings()
        
        if (settings.environment == "production" and 
            any("NOT using Supabase" in check for check in startup_summary['failed_checks'])):
            print("🔧 Production environment detected with SQLite - forcing Supabase mode...")
            if force_supabase_mode():
                print("✅ Supabase mode activated successfully")
            else:
                print("❌ Failed to activate Supabase mode")
        
        # Initialize database with smart backend selection
        from app.core.database_factory import database_factory
        await database_factory.initialize()
        
        db_info = database_factory.get_database_info()
        print(f"✅ Database Backend: {db_info['backend']}")
        
        # Initialize schema and data if needed
        if not database_factory.is_using_supabase:
            from app.init_db_unified import init_database
            print("🔧 Initializing SQLAlchemy schema and data...")
            db_success = await init_database()
            if db_success:
                print("✅ SQLAlchemy database initialized successfully")
            else:
                print("⚠️ SQLAlchemy database initialization had issues, but continuing...")
        else:
            print("📊 Using Supabase - ensure schema is set up in Supabase Dashboard")
            
    except Exception as e:
        print(f"⚠️ Startup initialization error: {e}")
        import traceback
        traceback.print_exc()
    
    print("📊 AIAlchemy API ready")
    yield
    # Shutdown
    print("🔒 Shutting down AIAlchemy API server...")
    try:
        await database_manager.disconnect()
        print("✅ Database disconnected")
    except Exception as e:
        print(f"⚠️ Database disconnect error: {e}")

# Create FastAPI app with large file upload support
app = FastAPI(
    title="AIAlchemy API",
    description="AI-powered startup evaluation platform with comprehensive REST API",
    version="1.0.0",
    lifespan=lifespan
)

# Add Security Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuthenticationMiddleware)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)  # Authentication routes (public)
app.include_router(dashboard.router)
app.include_router(startups.router)
app.include_router(pipeline.router)
app.include_router(memos.router)
app.include_router(uploads.router)
app.include_router(settings.router)
app.include_router(document_processing.router)  # New document processing pipeline
app.include_router(vector_documents.router)  # Vector database for document extraction
app.include_router(ai_models.router)  # Model-agnostic AI service management

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
            "settings": "/api/settings/",
            "document_processing": "/api/v1/document-processing/",
            "vector_documents": "/vector-documents/",
            "ai_models": "/ai-models/",
            "debug": "/debug/"
        },
        "features": [
            "Startup application management",
            "AI-powered evaluation pipeline",
            "Investment memo generation",
            "File upload and processing",
            "Comprehensive analytics dashboard",
            "User account management",
            "JWT-based authentication",
            "Role-based access control"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint with database backend detection"""
    from app.core.database_factory import database_factory
    
    try:
        # Get database information
        db_info = database_factory.get_database_info()
        
        # Check database health based on backend
        if database_factory.is_using_supabase:
            # Test Supabase connection
            try:
                from app.services.database_service import db_service
                if hasattr(db_service, 'supabase'):
                    # Test query to verify connection
                    result = db_service.supabase.table('users').select('count').limit(1).execute()
                    db_status = "connected"
                    tables_exist = True  # Assume Supabase tables exist
                else:
                    db_status = "supabase_not_initialized"
                    tables_exist = False
            except Exception as e:
                db_status = f"supabase_error: {str(e)}"
                tables_exist = False
        else:
            # Test SQLAlchemy connection
            from sqlalchemy import text
            db_status = "connected" if database_manager.is_connected else "disconnected" 
            tables_exist = False
            
            try:
                if database_manager.is_connected:
                    async with database_manager.get_session() as session:
                        # Check if startup_applications table exists
                        result = await session.execute(
                            text("SELECT name FROM sqlite_master WHERE type='table' AND name='startup_applications'")
                        )
                        tables_exist = result.fetchone() is not None
            except Exception as e:
                db_status = f"sqlalchemy_error: {str(e)}"
        
        return {
            "status": "healthy" if tables_exist else "degraded",
            "service": "aialchemy-backend",
            "database": {
                "backend": db_info["backend"],
                "status": db_status,
                "environment": db_info["environment"],
                "auto_detected": db_info.get("auto_detected", False),
                "tables_initialized": tables_exist
            },
            "timestamp": "2025-01-20T16:00:00Z"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "aialchemy-backend",
            "database": {"status": f"health_check_error: {str(e)}"},
            "timestamp": "2025-01-20T16:00:00Z"
        }

@app.get("/debug/database")
async def debug_database():
    """Debug endpoint to diagnose database configuration issues"""
    try:
        from app.core.config import get_settings
        from app.services.database_service import db_service
        from app.core.database_factory import database_factory
        
        settings = get_settings()
        
        # Gather diagnostic information
        debug_info = {
            "timestamp": "2025-01-20T16:00:00Z",
            "environment_variables": {
                "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT_SET"),
                "USE_SUPABASE": os.getenv("USE_SUPABASE", "NOT_SET"),
                "SUPABASE_URL": "SET" if os.getenv("SUPABASE_URL") else "NOT_SET",
                "SUPABASE_ANON_KEY": "SET" if os.getenv("SUPABASE_ANON_KEY") else "NOT_SET",
                "DATABASE_URL": settings.database_url if not settings.should_use_supabase else "USING_SUPABASE"
            },
            "configuration": {
                "settings_environment": settings.environment,
                "settings_use_supabase": settings.use_supabase,
                "settings_should_use_supabase": settings.should_use_supabase,
                "settings_database_url": settings.database_url[:50] + "..." if len(settings.database_url) > 50 else settings.database_url,
                "effective_database_url": settings.effective_database_url[:50] + "..." if len(settings.effective_database_url) > 50 else settings.effective_database_url
            },
            "database_service": {
                "db_service_use_supabase": db_service.use_supabase,
                "has_supabase_client": hasattr(db_service, 'supabase'),
            },
            "database_factory": database_factory.get_database_info()
        }
        
        # Test connections
        connection_tests = {}
        
        # Test Supabase if configured
        if settings.should_use_supabase:
            try:
                from app.core.supabase_client import get_supabase_client
                supabase = get_supabase_client()
                result = supabase.table('users').select('count').limit(1).execute()
                connection_tests["supabase"] = {
                    "status": "success",
                    "message": f"Connected successfully, {len(result.data) if result.data else 0} records"
                }
            except Exception as e:
                connection_tests["supabase"] = {
                    "status": "failed",
                    "message": str(e)
                }
        
        # Test SQLAlchemy if available
        try:
            from app.core.database import database_manager
            if database_manager.is_connected:
                connection_tests["sqlalchemy"] = {
                    "status": "success",
                    "message": "SQLAlchemy connected"
                }
            else:
                connection_tests["sqlalchemy"] = {
                    "status": "not_connected",
                    "message": "SQLAlchemy not connected"
                }
        except Exception as e:
            connection_tests["sqlalchemy"] = {
                "status": "failed",
                "message": str(e)
            }
        
        debug_info["connection_tests"] = connection_tests
        
        # Recommendations
        recommendations = []
        if settings.environment == "production" and not settings.should_use_supabase:
            recommendations.append("Production environment should use Supabase")
        if settings.should_use_supabase and not db_service.use_supabase:
            recommendations.append("Database service not using Supabase despite configuration")
        if not settings.supabase_url and settings.environment == "production":
            recommendations.append("Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        
        debug_info["recommendations"] = recommendations
        
        return debug_info
        
    except Exception as e:
        return {
            "error": f"Debug endpoint failed: {str(e)}",
            "timestamp": "2025-01-20T16:00:00Z"
        }

@app.post("/debug/force-supabase")
async def force_supabase():
    """Force the application to use Supabase (admin endpoint)"""
    try:
        from app.startup_checks import force_supabase_mode
        
        success = force_supabase_mode()
        
        if success:
            return {
                "status": "success",
                "message": "Forced Supabase mode activated",
                "timestamp": "2025-01-20T16:00:00Z"
            }
        else:
            return {
                "status": "failed", 
                "message": "Could not activate Supabase mode - check credentials",
                "timestamp": "2025-01-20T16:00:00Z"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Force Supabase failed: {str(e)}",
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
            ],
            "auth": [
                "POST /api/auth/login",
                "POST /api/auth/register",
                "POST /api/auth/refresh",
                "POST /api/auth/logout",
                "GET /api/auth/me"
            ]
        }
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)