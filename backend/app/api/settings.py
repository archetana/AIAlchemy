"""
User settings API endpoints for AIAlchemy.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session

router = APIRouter()


@router.get("/")
async def get_user_settings(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get user preferences and settings.
    """
    # TODO: Implement settings logic
    return {"theme": "dark", "notifications": True}