#!/usr/bin/env python3
"""
Quick test endpoint to verify GCS integration is working.
Run this to test the file storage service before building the full upload system.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from app.core.config import get_settings

def create_test_app():
    """Create a minimal FastAPI app to test GCS integration."""
    
    app = FastAPI(title="AIAlchemy GCS Test", version="1.0.0")
    settings = get_settings()
    
    @app.get("/")
    async def root():
        """Root endpoint with basic info."""
        return {
            "message": "AIAlchemy GCS Test API",
            "gcs_enabled": settings.use_google_cloud_storage,
            "bucket": settings.google_cloud_storage_bucket if settings.use_google_cloud_storage else "local",
            "status": "ready"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "gcs_configured": settings.use_google_cloud_storage,
            "project": settings.google_cloud_project if settings.use_google_cloud_storage else None
        }
    
    @app.get("/gcs-config")
    async def gcs_config():
        """Get GCS configuration (without sensitive data)."""
        
        if not settings.use_google_cloud_storage:
            return {
                "gcs_enabled": False,
                "storage_mode": "local",
                "local_path": settings.local_upload_path
            }
        
        # Check if credentials file exists
        creds_path = Path(settings.google_application_credentials or "")
        creds_exists = creds_path.exists() if settings.google_application_credentials else False
        
        return {
            "gcs_enabled": True,
            "storage_mode": "google_cloud_storage", 
            "project": settings.google_cloud_project,
            "bucket": settings.google_cloud_storage_bucket,
            "credentials_file_exists": creds_exists,
            "credentials_path": str(creds_path) if creds_exists else "not found",
            "max_file_size_mb": settings.max_upload_size_mb
        }
    
    @app.get("/test-gcs")
    async def test_gcs_connection():
        """Test actual GCS connection (requires google-cloud-storage package)."""
        
        if not settings.use_google_cloud_storage:
            raise HTTPException(
                status_code=400,
                detail="GCS not enabled. Set USE_GOOGLE_CLOUD_STORAGE=true"
            )
        
        try:
            from google.cloud import storage
            from google.auth.exceptions import DefaultCredentialsError
            
            # Test authentication and bucket access
            client = storage.Client()
            bucket_name = settings.google_cloud_storage_bucket
            bucket = client.bucket(bucket_name)
            
            # Test if bucket exists and is accessible
            exists = bucket.exists()
            
            if not exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"Bucket gs://{bucket_name} not found or not accessible"
                )
            
            # Test write permissions with a small test
            test_blob = bucket.blob("test-connection/health-check.txt")
            test_content = "AIAlchemy GCS connection test"
            test_blob.upload_from_string(test_content)
            
            # Test read permissions
            downloaded = test_blob.download_as_text()
            
            # Clean up
            test_blob.delete()
            
            return {
                "status": "success",
                "message": "GCS connection successful",
                "bucket": f"gs://{bucket_name}",
                "permissions": ["read", "write", "delete"],
                "test_completed": True
            }
            
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="google-cloud-storage package not installed. Run: pip install google-cloud-storage"
            )
        except DefaultCredentialsError as e:
            raise HTTPException(
                status_code=401, 
                detail=f"GCS authentication failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"GCS test failed: {str(e)}"
            )
    
    return app

def main():
    """Run the test server."""
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please create it first.")
        print("📋 See: COMPLETE_GCS_SETUP.md for instructions")
        sys.exit(1)
    
    # Create and run the app
    app = create_test_app()
    
    print("🚀 Starting AIAlchemy GCS Test Server...")
    print("📍 Endpoints available:")
    print("   - http://localhost:8000/ - Basic info")  
    print("   - http://localhost:8000/health - Health check")
    print("   - http://localhost:8000/gcs-config - GCS configuration")
    print("   - http://localhost:8000/test-gcs - Test GCS connection")
    print("")
    print("⏹️  Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()