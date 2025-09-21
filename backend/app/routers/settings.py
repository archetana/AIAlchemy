"""
Settings API endpoints
Handles user account settings and system configuration
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.crud import user_crud, industry_crud
from app.schemas import User, UserUpdate, Industry, InvestmentWeights
from app.models import User as UserModel
from app.models import InvestmentWeights as InvestmentWeightsModel

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/users/me", response_model=User)
async def get_current_user(
    user_id: int = 1,  # Simplified - in production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile information
    """
    try:
        user = await user_crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")

@router.put("/users/me", response_model=User)
async def update_current_user(
    user_data: UserUpdate,
    user_id: int = 1,  # Simplified - in production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile information
    """
    try:
        from sqlalchemy import select
        
        # Get current user
        query = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user data
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

@router.get("/users", response_model=List[User])
async def get_all_users(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (for admin settings)
    """
    try:
        users = await user_crud.get_all_users(db)
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/industries", response_model=List[Industry])
async def get_all_industries(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all industries for configuration
    """
    try:
        industries = await industry_crud.get_all_industries(db)
        return industries
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch industries: {str(e)}")

@router.get("/investment-weights", response_model=InvestmentWeights)
async def get_investment_weights(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current investment criteria weights
    """
    try:
        from sqlalchemy import select, desc
        
        query = select(InvestmentWeightsModel).where(
            InvestmentWeightsModel.is_active == True
        ).order_by(desc(InvestmentWeightsModel.created_at)).limit(1)
        
        result = await db.execute(query)
        weights = result.scalar_one_or_none()
        
        if not weights:
            # Return default weights if none exist
            return InvestmentWeights(
                market_size_weight=25.0,
                team_experience_weight=30.0,
                business_model_weight=20.0,
                traction_weight=15.0,
                financial_health_weight=10.0
            )
        
        return weights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch investment weights: {str(e)}")

@router.put("/investment-weights", response_model=InvestmentWeights)
async def update_investment_weights(
    weights_data: InvestmentWeights,
    user_id: int = 1,  # Simplified - in production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Update investment criteria weights
    """
    try:
        # Validate weights sum to 100
        total_weight = (
            weights_data.market_size_weight +
            weights_data.team_experience_weight +
            weights_data.business_model_weight +
            weights_data.traction_weight +
            weights_data.financial_health_weight
        )
        
        if abs(total_weight - 100.0) > 0.1:  # Allow small floating point differences
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to 100. Current sum: {total_weight}"
            )
        
        # Deactivate existing weights
        from sqlalchemy import update
        await db.execute(
            update(InvestmentWeightsModel).values(is_active=False)
        )
        
        # Create new weights record
        weights = InvestmentWeightsModel(
            market_size_weight=weights_data.market_size_weight,
            team_experience_weight=weights_data.team_experience_weight,
            business_model_weight=weights_data.business_model_weight,
            traction_weight=weights_data.traction_weight,
            financial_health_weight=weights_data.financial_health_weight,
            created_by_id=user_id,
            is_active=True
        )
        
        db.add(weights)
        await db.commit()
        await db.refresh(weights)
        
        return weights
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update investment weights: {str(e)}")

@router.get("/account/preferences")
async def get_account_preferences(
    user_id: int = 1,  # Simplified - in production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Get user account preferences
    """
    try:
        user = await user_crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return account preferences (expandable)
        preferences = {
            "notifications": {
                "email_notifications": True,
                "desktop_notifications": True,
                "weekly_reports": True
            },
            "display": {
                "theme": "light",
                "language": "en",
                "timezone": "UTC"
            },
            "privacy": {
                "profile_visibility": "team",
                "share_analytics": True
            }
        }
        
        return {
            "success": True,
            "data": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preferences: {str(e)}")

@router.put("/account/preferences")
async def update_account_preferences(
    preferences: dict,
    user_id: int = 1,  # Simplified - in production, get from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Update user account preferences
    """
    try:
        user = await user_crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # In production, you would store preferences in a separate table
        # For now, just return success
        
        return {
            "success": True,
            "data": {
                "message": "Preferences updated successfully",
                "updated_preferences": preferences
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@router.get("/system/info")
async def get_system_info(
    db: AsyncSession = Depends(get_db)
):
    """
    Get system information and health
    """
    try:
        from sqlalchemy import select, func, text
        from app.models import StartupApplication, User as UserModel, InvestmentMemo
        
        # Database statistics
        startups_count_query = select(func.count(StartupApplication.id))
        startups_result = await db.execute(startups_count_query)
        startups_count = startups_result.scalar() or 0
        
        users_count_query = select(func.count(UserModel.id))
        users_result = await db.execute(users_count_query)
        users_count = users_result.scalar() or 0
        
        memos_count_query = select(func.count(InvestmentMemo.id))
        memos_result = await db.execute(memos_count_query)
        memos_count = memos_result.scalar() or 0
        
        # Database size (SQLite specific)
        try:
            db_size_query = text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();")
            db_size_result = await db.execute(db_size_query)
            db_size_bytes = db_size_result.scalar() or 0
        except:
            db_size_bytes = 0
        
        system_info = {
            "database": {
                "type": "SQLite",
                "size_mb": round(db_size_bytes / (1024 * 1024), 2),
                "startups_count": startups_count,
                "users_count": users_count,
                "memos_count": memos_count
            },
            "application": {
                "name": "AIAlchemy API",
                "version": "1.0.0",
                "environment": "development"
            },
            "features": {
                "file_uploads": True,
                "ai_processing": True,
                "pipeline_management": True,
                "investment_memos": True,
                "analytics_dashboard": True
            }
        }
        
        return {
            "success": True,
            "data": system_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch system info: {str(e)}")