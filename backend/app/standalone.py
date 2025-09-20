"""
Completely standalone FastAPI app for deployment verification
No imports from existing codebase to avoid any database connections
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create completely fresh FastAPI app
app = FastAPI(
    title="AIAlchemy API - Standalone",
    description="Minimal API for deployment verification",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - completely standalone"""
    return {
        "service": "AIAlchemy Backend",
        "status": "running", 
        "version": "1.0.0",
        "mode": "standalone",
        "message": "Deployment verification successful!",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health():
    """Health check for Cloud Run"""
    return {
        "status": "healthy",
        "service": "aialchemy-backend",
        "mode": "standalone"
    }

@app.get("/api/test")
async def api_test():
    """Test API endpoint"""
    return {
        "api": "working",
        "endpoints": ["/", "/health", "/api/test"],
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "port": os.getenv("PORT", "8000")
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("standalone:app", host="0.0.0.0", port=port)