"""
Simple FastAPI application for deployment verification
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AIAlchemy API",
    description="AI-powered startup evaluation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AIAlchemy API",
        "version": "1.0.0",
        "status": "running",
        "message": "Backend deployment successful!"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {"status": "healthy", "service": "aialchemy-backend"}

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "endpoints": ["/", "/health", "/api/status"],
        "deployment": "cloud-run"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main_simple:app", host="0.0.0.0", port=port)