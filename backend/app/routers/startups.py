"""
Startup Applications API endpoints
Handles CRUD operations for startup applications with pagination and filtering
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.crud import startup_crud
from app.schemas import (
    StartupApplication, StartupApplicationCreate, StartupApplicationUpdate,
    PaginatedStartups, StartupFilters, PaginationParams
)
from app.models import ApplicationStatus, FundingStage

router = APIRouter(prefix="/api/startups", tags=["startups"])

@router.get("/")
async def get_startups(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    
    # Sorting parameters
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    
    # Filter parameters
    status: Optional[ApplicationStatus] = Query(None, description="Filter by application status"),
    industry_id: Optional[int] = Query(None, description="Filter by industry ID"),
    funding_stage: Optional[FundingStage] = Query(None, description="Filter by funding stage"),
    assigned_analyst_id: Optional[int] = Query(None, description="Filter by assigned analyst"),
    min_ai_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum AI score"),
    max_ai_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum AI score"),
    search: Optional[str] = Query(None, description="Search in company name, contact name, or email"),
    
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of startup applications with filtering and sorting
    
    Supports:
    - Pagination with configurable page size
    - Filtering by status, industry, funding stage, analyst, AI score
    - Text search across company name, contact name, and email
    - Sorting by any field with asc/desc order
    """
    try:
        filters = StartupFilters(
            status=status,
            industry_id=industry_id,
            funding_stage=funding_stage,
            assigned_analyst_id=assigned_analyst_id,
            min_ai_score=min_ai_score,
            max_ai_score=max_ai_score,
            search=search
        )
        
        pagination = PaginationParams(page=page, page_size=page_size)
        
        result = await startup_crud.get_startups_paginated(
            db, filters, pagination, sort_by, sort_order
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch startups: {str(e)}")

@router.get("/{startup_id}", response_model=StartupApplication)
async def get_startup_by_id(
    startup_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific startup application
    Includes all related data: founders, files, metrics, memo, history
    """
    try:
        startup = await startup_crud.get_startup_by_id(db, startup_id)
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        return startup
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch startup: {str(e)}")

@router.post("/")
async def create_startup(
    startup_data: StartupApplicationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new startup application
    """
    try:
        startup = await startup_crud.create_startup(db, startup_data)
        return {"success": True, "data": startup, "message": "Startup application created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create startup: {str(e)}")

@router.put("/{startup_id}", response_model=StartupApplication)
async def update_startup(
    startup_id: int,
    startup_data: StartupApplicationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing startup application
    """
    try:
        startup = await startup_crud.update_startup(db, startup_id, startup_data)
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        return startup
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update startup: {str(e)}")

@router.get("/status/{status}/count")
async def get_startups_count_by_status(
    status: ApplicationStatus,
    db: AsyncSession = Depends(get_db)
):
    """
    Get count of startups by specific status
    Fast endpoint for status counters
    """
    try:
        filters = StartupFilters(status=status)
        pagination = PaginationParams(page=1, page_size=1)  # We only need the count
        
        result = await startup_crud.get_startups_paginated(db, filters, pagination)
        
        return {
            "success": True,
            "data": {
                "status": status.value,
                "count": result.total
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count startups: {str(e)}")

@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of suggestions"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get search suggestions for startup names
    Fast autocomplete endpoint
    """
    try:
        filters = StartupFilters(search=query)
        pagination = PaginationParams(page=1, page_size=limit)
        
        result = await startup_crud.get_startups_paginated(db, filters, pagination)
        
        suggestions = [
            {
                "id": startup.id,
                "company_name": startup.company_name,
                "status": startup.status.value,
                "industry": startup.industry.name if startup.industry else None
            }
            for startup in result.items
        ]
        
        return {
            "success": True,
            "data": suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")