"""
Authentication Dependencies for FastAPI Endpoints
Provides authentication, authorization, and user context dependencies
"""

from typing import Optional, List, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db_session
from app.models import User, UserRole
from app.auth.jwt_handler import jwt_handler
import structlog

logger = structlog.get_logger()

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Get current user from JWT token (optional - returns None if no token)
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User object or None if no valid token
    """
    if not credentials:
        return None
    
    try:
        # Verify JWT token
        payload = jwt_handler.verify_token(credentials.credentials)
        if not payload:
            return None
        
        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user from database
        query = select(User).where(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        logger.info("User authenticated", user_id=user.id, email=user.email)
        return user
        
    except Exception as e:
        logger.warning("Authentication failed", error=str(e))
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Get current user from JWT token (required - raises 401 if no valid token)
    
    Args:
        credentials: HTTP Bearer token credentials (required)
        db: Database session
        
    Returns:
        User object
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    if not credentials:
        logger.warning("No credentials provided")
        raise AuthenticationError("No authentication token provided")
    
    try:
        # Verify JWT token
        payload = jwt_handler.verify_token(credentials.credentials)
        if not payload:
            logger.warning("Invalid JWT token")
            raise AuthenticationError("Invalid authentication token")
        
        # Check token type
        if payload.get("type") != "access":
            logger.warning("Wrong token type", token_type=payload.get("type"))
            raise AuthenticationError("Invalid token type")
        
        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("No user ID in token")
            raise AuthenticationError("Invalid token payload")
        
        # Get user from database
        query = select(User).where(User.id == int(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning("User not found", user_id=user_id)
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            logger.warning("User account disabled", user_id=user.id)
            raise AuthenticationError("Account disabled")
        
        logger.info("User authenticated", user_id=user.id, email=user.email)
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise AuthenticationError("Authentication failed")

def require_roles(*required_roles: UserRole):
    """
    Dependency factory for role-based access control
    
    Args:
        *required_roles: Required user roles (Admin, Partner, Analyst, Viewer)
        
    Returns:
        Dependency function that checks user role
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            logger.warning(
                "Insufficient permissions", 
                user_id=current_user.id,
                user_role=current_user.role,
                required_roles=[role.value for role in required_roles]
            )
            raise AuthorizationError(
                f"Insufficient permissions. Required roles: {[role.value for role in required_roles]}"
            )
        
        logger.info(
            "Role authorization successful",
            user_id=current_user.id,
            user_role=current_user.role
        )
        return current_user
    
    return role_checker

def require_admin():
    """Require Admin role"""
    return require_roles(UserRole.ADMIN)

def require_admin_or_partner():
    """Require Admin or Partner role"""
    return require_roles(UserRole.ADMIN, UserRole.PARTNER)

def require_admin_or_analyst():
    """Require Admin or Analyst role"""
    return require_roles(UserRole.ADMIN, UserRole.ANALYST)

def require_any_role():
    """Require any authenticated user (any role)"""
    return require_roles(UserRole.ADMIN, UserRole.PARTNER, UserRole.ANALYST, UserRole.VIEWER)

class PermissionChecker:
    """Advanced permission checking for complex authorization logic"""
    
    @staticmethod
    def can_view_startup(user: User, startup_id: int) -> bool:
        """Check if user can view a specific startup"""
        # Admin and Partners can view all
        if user.role in [UserRole.ADMIN, UserRole.PARTNER]:
            return True
        
        # Analysts can view assigned startups
        # TODO: Implement startup assignment logic
        return user.role == UserRole.ANALYST
    
    @staticmethod
    def can_edit_startup(user: User, startup_id: int) -> bool:
        """Check if user can edit a specific startup"""
        # Only Admin and assigned Analyst can edit
        if user.role == UserRole.ADMIN:
            return True
        
        # TODO: Check if analyst is assigned to this startup
        return user.role == UserRole.ANALYST
    
    @staticmethod
    def can_approve_memo(user: User) -> bool:
        """Check if user can approve investment memos"""
        return user.role in [UserRole.ADMIN, UserRole.PARTNER]
    
    @staticmethod
    def can_manage_users(user: User) -> bool:
        """Check if user can manage other users"""
        return user.role == UserRole.ADMIN

# Convenience dependencies
def get_permission_checker(current_user: User = Depends(get_current_user)) -> PermissionChecker:
    """Get permission checker with current user context"""
    return PermissionChecker()

async def get_refresh_token_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Get user from refresh token (for token refresh endpoint)
    
    Args:
        credentials: HTTP Bearer refresh token credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        AuthenticationError: If refresh token is invalid
    """
    if not credentials:
        raise AuthenticationError("No refresh token provided")
    
    try:
        # Verify it's a refresh token
        if not jwt_handler.is_token_type(credentials.credentials, "refresh"):
            raise AuthenticationError("Invalid token type - refresh token required")
        
        # Get user ID from refresh token
        user_id = jwt_handler.extract_user_id(credentials.credentials)
        if not user_id:
            raise AuthenticationError("Invalid refresh token")
        
        # Get user from database
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or disabled")
        
        logger.info("Refresh token validated", user_id=user.id)
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Refresh token validation failed", error=str(e))
        raise AuthenticationError("Invalid refresh token")