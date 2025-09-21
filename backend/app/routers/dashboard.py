"""
Dashboard API endpoints
Provides metrics and overview data for the dashboard screen
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.crud import dashboard_crud
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics
    
    Returns:
    - Total applications count
    - Applications in AI processing
    - Completed evaluations count  
    - Average AI score
    - Recent applications (last 10)
    - Pipeline metrics
    """
    try:
        stats = await dashboard_crud.get_dashboard_stats(db)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")

@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard overview with key metrics
    Optimized for fast loading
    """
    try:
        stats = await dashboard_crud.get_dashboard_stats(db)
        
        # Return simplified overview for fast loading
        return {
            "success": True,
            "data": {
                "total_applications": stats["total_applications"],
                "ai_processing": stats["ai_processing"],
                "completed_analysis": stats["completed_analysis"],
                "average_score": stats["average_score"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard overview: {str(e)}")