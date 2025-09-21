"""
Investment Memos API endpoints
Handles investment memo CRUD operations and document management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.crud import memo_crud, startup_crud
from app.schemas import (
    InvestmentMemo, InvestmentMemoCreate, InvestmentMemoUpdate,
    PaginatedMemos
)

router = APIRouter(prefix="/api/memos", tags=["memos"])

@router.get("/startup/{startup_id}", response_model=InvestmentMemo)
async def get_memo_by_startup(
    startup_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get investment memo for a specific startup
    """
    try:
        memo = await memo_crud.get_memo_by_startup_id(db, startup_id)
        if not memo:
            # Check if startup exists
            startup = await startup_crud.get_startup_by_id(db, startup_id)
            if not startup:
                raise HTTPException(status_code=404, detail="Startup not found")
            raise HTTPException(status_code=404, detail="Investment memo not found for this startup")
        
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch memo: {str(e)}")

@router.post("/", response_model=InvestmentMemo)
async def create_memo(
    memo_data: InvestmentMemoCreate,
    author_id: int = Query(..., description="ID of the memo author"),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new investment memo
    """
    try:
        # Verify startup exists
        startup = await startup_crud.get_startup_by_id(db, memo_data.startup_application_id)
        if not startup:
            raise HTTPException(status_code=404, detail="Startup not found")
        
        # Check if memo already exists for this startup
        existing_memo = await memo_crud.get_memo_by_startup_id(db, memo_data.startup_application_id)
        if existing_memo:
            raise HTTPException(status_code=400, detail="Investment memo already exists for this startup")
        
        memo = await memo_crud.create_memo(db, memo_data, author_id)
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memo: {str(e)}")

@router.put("/{memo_id}", response_model=InvestmentMemo)
async def update_memo(
    memo_id: int,
    memo_data: InvestmentMemoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing investment memo
    """
    try:
        memo = await memo_crud.update_memo(db, memo_id, memo_data)
        if not memo:
            raise HTTPException(status_code=404, detail="Investment memo not found")
        
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update memo: {str(e)}")

@router.get("/", response_model=List[InvestmentMemo])
async def get_memos(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_draft: Optional[bool] = Query(None, description="Filter by draft status"),
    approved: Optional[bool] = Query(None, description="Filter by approval status"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of investment memos with filtering
    """
    try:
        from sqlalchemy import select, and_, desc
        from sqlalchemy.orm import joinedload
        
        # Build query with filters
        query = select(InvestmentMemo).options(
            joinedload(InvestmentMemo.author),
            joinedload(InvestmentMemo.startup_application)
        )
        
        conditions = []
        if is_draft is not None:
            conditions.append(InvestmentMemo.is_draft == is_draft)
        if approved is not None:
            conditions.append(InvestmentMemo.approved == approved)
        if author_id is not None:
            conditions.append(InvestmentMemo.author_id == author_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply sorting and pagination
        query = query.order_by(desc(InvestmentMemo.updated_at))
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        memos = result.scalars().all()
        
        return memos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch memos: {str(e)}")

@router.get("/{memo_id}", response_model=InvestmentMemo)
async def get_memo_by_id(
    memo_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific investment memo by ID
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        
        query = select(InvestmentMemo).options(
            joinedload(InvestmentMemo.author),
            joinedload(InvestmentMemo.startup_application).joinedload('industry'),
            joinedload(InvestmentMemo.startup_application).joinedload('founders')
        ).where(InvestmentMemo.id == memo_id)
        
        result = await db.execute(query)
        memo = result.scalar_one_or_none()
        
        if not memo:
            raise HTTPException(status_code=404, detail="Investment memo not found")
        
        return memo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch memo: {str(e)}")

@router.post("/{memo_id}/approve")
async def approve_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Approve an investment memo
    """
    try:
        memo_data = InvestmentMemoUpdate(
            approved=True,
            is_draft=False
        )
        
        memo = await memo_crud.update_memo(db, memo_id, memo_data)
        if not memo:
            raise HTTPException(status_code=404, detail="Investment memo not found")
        
        return {
            "success": True,
            "data": {
                "memo_id": memo_id,
                "approved": True,
                "approved_at": memo.updated_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve memo: {str(e)}")

@router.post("/{memo_id}/schedule-review")
async def schedule_partner_review(
    memo_id: int,
    review_date: str = Query(..., description="Review date in ISO format (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule partner review for an investment memo
    """
    try:
        from datetime import datetime
        
        # Parse review date
        try:
            parsed_date = datetime.fromisoformat(review_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        memo_data = InvestmentMemoUpdate(
            partner_review_scheduled=True,
            partner_review_date=parsed_date
        )
        
        memo = await memo_crud.update_memo(db, memo_id, memo_data)
        if not memo:
            raise HTTPException(status_code=404, detail="Investment memo not found")
        
        return {
            "success": True,
            "data": {
                "memo_id": memo_id,
                "review_scheduled": True,
                "review_date": parsed_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule review: {str(e)}")

@router.get("/stats/summary")
async def get_memo_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get investment memo statistics
    """
    try:
        from sqlalchemy import select, func
        
        # Total memos
        total_query = select(func.count(InvestmentMemo.id))
        total_result = await db.execute(total_query)
        total_memos = total_result.scalar() or 0
        
        # Draft memos
        draft_query = select(func.count(InvestmentMemo.id)).where(
            InvestmentMemo.is_draft == True
        )
        draft_result = await db.execute(draft_query)
        draft_memos = draft_result.scalar() or 0
        
        # Approved memos
        approved_query = select(func.count(InvestmentMemo.id)).where(
            InvestmentMemo.approved == True
        )
        approved_result = await db.execute(approved_query)
        approved_memos = approved_result.scalar() or 0
        
        # Pending review
        pending_query = select(func.count(InvestmentMemo.id)).where(
            InvestmentMemo.partner_review_scheduled == True,
            InvestmentMemo.approved == False
        )
        pending_result = await db.execute(pending_query)
        pending_review = pending_result.scalar() or 0
        
        return {
            "success": True,
            "data": {
                "total_memos": total_memos,
                "draft_memos": draft_memos,
                "approved_memos": approved_memos,
                "pending_review": pending_review,
                "completion_rate": round((approved_memos / total_memos * 100) if total_memos > 0 else 0, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch memo stats: {str(e)}")