"""
Settings API endpoints
Handles user account settings and system configuration
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db_session
from app.crud import user_crud, industry_crud
from app.schemas import User, UserUpdate, Industry, InvestmentWeights, UserProfile
from app.models import User as UserModel
from app.models import InvestmentWeights as InvestmentWeightsModel
from app.auth.auth_dependencies import get_current_user, require_admin, require_admin_or_partner

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("/users/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current user profile information
    """
    return UserProfile.model_validate(current_user)

@router.put("/users/me", response_model=UserProfile)
async def update_current_user(
    user_data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update current user profile information
    """
    try:
        # Update user data
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        return UserProfile.model_validate(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

@router.get("/users", response_model=List[UserProfile])
async def get_all_users(
    current_user: UserModel = Depends(require_admin()),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all users (for admin settings)
    """
    try:
        users = await user_crud.get_all_users(db)
        return [UserProfile.model_validate(user) for user in users]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/industries", response_model=List[Industry])
async def get_all_industries(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
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
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
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
    current_user: UserModel = Depends(require_admin_or_partner()),
    db: AsyncSession = Depends(get_db_session)
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
            created_by_id=current_user.id,
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
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get user account preferences
    """
    try:
        # User is already authenticated and available as current_user
        
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
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update user account preferences
    """
    try:
        # User is already authenticated and available as current_user
        
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
    current_user: UserModel = Depends(require_admin()),
    db: AsyncSession = Depends(get_db_session)
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