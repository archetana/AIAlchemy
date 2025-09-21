"""
Deal Pipeline API endpoints
Provides pipeline statistics and workflow management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.database import get_db
from app.crud import pipeline_crud, startup_crud
from app.schemas import StartupFilters, PaginationParams
from app.models import ApplicationStatus

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_pipeline_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive deal pipeline statistics
    
    Returns:
    - Applications count by status/stage
    - Conversion rates between stages
    - Average days spent in each stage
    - Current bottlenecks
    - Weekly throughput metrics
    """
    try:
        stats = await pipeline_crud.get_pipeline_stats(db)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pipeline stats: {str(e)}")

@router.get("/stages")
async def get_pipeline_stages(
    db: AsyncSession = Depends(get_db)
):
    """
    Get applications grouped by pipeline stages
    Returns detailed view for Kanban board
    """
    try:
        stages = {}
        
        # Get applications for each status
        for status in ApplicationStatus:
            filters = StartupFilters(status=status)
            pagination = PaginationParams(page=1, page_size=50)  # Limit for performance
            
            result = await startup_crud.get_startups_paginated(
                db, filters, pagination, sort_by="updated_at", sort_order="desc"
            )
            
            stages[status.value] = {
                "count": result.total,
                "applications": [
                    {
                        "id": app.id,
                        "company_name": app.company_name,
                        "industry": app.industry.name if app.industry else None,
                        "funding_stage": app.funding_stage.value if app.funding_stage else None,
                        "ai_score": app.ai_score,
                        "assigned_analyst": app.assigned_analyst.full_name if app.assigned_analyst else None,
                        "created_at": app.created_at,
                        "updated_at": app.updated_at
                    }
                    for app in result.items
                ]
            }
        
        return {
            "success": True,
            "data": stages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pipeline stages: {str(e)}")

@router.get("/bottlenecks")
async def get_pipeline_bottlenecks(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current pipeline bottlenecks analysis
    Fast endpoint for bottleneck identification
    """
    try:
        stats = await pipeline_crud.get_pipeline_stats(db)
        bottlenecks = stats.get("bottlenecks", {})
        
        # Add additional context for each bottleneck
        bottleneck_details = []
        for status, count in bottlenecks.items():
            avg_days = stats.get("avg_days_per_stage", {}).get(status, 0)
            bottleneck_details.append({
                "status": status,
                "count": count,
                "avg_days": avg_days,
                "severity": "high" if count > 5 and avg_days > 3 else "medium" if count > 3 else "low"
            })
        
        return {
            "success": True,
            "data": {
                "bottlenecks": bottleneck_details,
                "total_bottlenecked": sum(bottlenecks.values()),
                "recommendations": [
                    "Allocate more resources to AI analysis stage" if "ai_analysis" in bottlenecks else None,
                    "Schedule more partner review meetings" if "partner_review" in bottlenecks else None,
                    "Improve data processing automation" if "data_processing" in bottlenecks else None
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze bottlenecks: {str(e)}")

@router.get("/throughput")
async def get_throughput_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get throughput metrics for specified time period
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import select, func, and_
        from app.models import StartupApplication
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Applications submitted in period
        submitted_query = select(func.count(StartupApplication.id)).where(
            StartupApplication.submitted_at.between(start_date, end_date)
        )
        submitted_result = await db.execute(submitted_query)
        submitted_count = submitted_result.scalar() or 0
        
        # Applications completed in period  
        completed_query = select(func.count(StartupApplication.id)).where(
            and_(
                StartupApplication.status == ApplicationStatus.COMPLETED,
                StartupApplication.completed_at.between(start_date, end_date)
            )
        )
        completed_result = await db.execute(completed_query)
        completed_count = completed_result.scalar() or 0
        
        # Calculate rates
        daily_submission_rate = submitted_count / days
        daily_completion_rate = completed_count / days
        completion_percentage = (completed_count / submitted_count * 100) if submitted_count > 0 else 0
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "submitted_applications": submitted_count,
                "completed_applications": completed_count,
                "daily_submission_rate": round(daily_submission_rate, 2),
                "daily_completion_rate": round(daily_completion_rate, 2),
                "completion_percentage": round(completion_percentage, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch throughput metrics: {str(e)}")

@router.put("/applications/{startup_id}/status")
async def update_application_status(
    startup_id: int,
    new_status: ApplicationStatus,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update application status (for pipeline management)
    Creates evaluation history record
    """
    try:
        from app.schemas import StartupApplicationUpdate
        from app.models import EvaluationHistory
        from datetime import datetime
        
        # Get current startup
        startup = await startup_crud.get_startup_by_id(db, startup_id)
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        
        old_status = startup.status
        
        # Update status
        update_data = StartupApplicationUpdate(status=new_status)
        updated_startup = await startup_crud.update_startup(db, startup_id, update_data)
        
        # Create evaluation history record
        history = EvaluationHistory(
            startup_application_id=startup_id,
            previous_status=old_status,
            new_status=new_status,
            notes=notes or f"Status changed from {old_status.value} to {new_status.value}",
            created_at=datetime.now()
        )
        
        db.add(history)
        await db.commit()
        
        return {
            "success": True,
            "data": {
                "startup_id": startup_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "updated_at": updated_startup.updated_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")