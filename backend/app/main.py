"""
AIAlchemy FastAPI Backend
AI-powered startup evaluation platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI app
app = FastAPI(
    title="AIAlchemy API",
    description="AI-powered startup evaluation platform",
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
    """Root endpoint"""
    return {
        "service": "AIAlchemy API",
        "status": "running", 
        "version": "1.0.0",
        "message": "Welcome to AIAlchemy - AI-powered startup evaluation platform",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "aialchemy-backend",
        "timestamp": "2025-01-20T16:00:00Z"
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api": "operational",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/api/status"],
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("standalone:app", host="0.0.0.0", port=port)