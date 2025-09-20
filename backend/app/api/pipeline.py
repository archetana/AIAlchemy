"""
Deal pipeline management API endpoints for AIAlchemy.
"""

from typing import Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session

router = APIRouter()


class PipelineStage(BaseModel):
    """Pipeline stage model."""
    name: str
    count: int
    items: List[Dict]


@router.get("/")
async def get_pipeline_overview(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get complete pipeline overview with all stages.
    """
    # TODO: Implement pipeline logic
    return {
        "stages": {
            "new_applications": 24,
            "processing": 8,
            "interview_scheduled": 5,
            "final_review": 6,
            "decided": 12
        }
    }


@router.patch("/{evaluation_id}/stage")
async def update_evaluation_stage(
    evaluation_id: str,
    stage_data: Dict,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Move evaluation to different pipeline stage.
    """
    # TODO: Implement stage update logic
    return {"message": "Stage updated successfully"}