"""
Authentication API endpoints for AIAlchemy
Handles user registration, login, logout, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db_session
from app.models import User, UserRole
from app.schemas import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    RefreshTokenRequest, RefreshTokenResponse, UserProfile,
    PasswordChangeRequest, PasswordResetRequest
)
from app.auth.jwt_handler import jwt_handler
from app.auth.password_utils import password_utils, hash_password, verify_password
from app.auth.simple_password import simple_password_utils, simple_hash_password, simple_verify_password
from app.auth.auth_dependencies import (
    get_current_user, get_refresh_token_user, AuthenticationError
)
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user account
    
    Args:
        user_data: Registration data (email, password, full_name, etc.)
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        Registration success response with user profile
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    try:
        # Check if email already exists
        existing_user_query = select(User).where(User.email == user_data.email)
        existing_user_result = await db.execute(existing_user_query)
        existing_user = existing_user_result.scalar_one_or_none()
        
        if existing_user:
            logger.warning("Registration attempt with existing email", email=user_data.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
            )
        
        # Validate and hash password with multiple fallback mechanisms
        password_validation = None
        
        # Method 1: Try passlib-based password utils (primary)
        try:
            password_validation = password_utils.validate_and_hash_password(user_data.password)
            logger.info("Primary passlib password hashing succeeded")
        except Exception as e:
            logger.warning("Primary passlib password hashing failed, trying simple bcrypt", error=str(e))
            
            # Method 2: Try simple bcrypt utils (fallback 1)
            try:
                password_validation = simple_password_utils.validate_and_hash_password(user_data.password)
                logger.info("Simple bcrypt password hashing succeeded")
            except Exception as e2:
                logger.warning("Simple bcrypt hashing failed, trying direct approach", error=str(e2))
                
                # Method 3: Manual validation + direct bcrypt (fallback 2)
                try:
                    validation_result = simple_password_utils.validator.validate_password(user_data.password)
                    if not validation_result["valid"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "message": "Password does not meet security requirements",
                                "errors": validation_result["errors"]
                            }
                        )
                    
                    # Try direct hashing
                    hashed_password = simple_hash_password(user_data.password)
                    password_validation = {
                        "valid": True,
                        "hashed_password": hashed_password,
                        "errors": []
                    }
                    logger.info("Direct bcrypt password hashing succeeded")
                except Exception as e3:
                    logger.error("All password hashing methods failed", 
                               primary_error=str(e), 
                               simple_error=str(e2), 
                               direct_error=str(e3))
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Password processing failed. Please try again or contact support."
                    )
        
        if not password_validation["valid"]:
            logger.warning("Invalid password in registration", errors=password_validation["errors"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements", 
                    "errors": password_validation["errors"]
                }
            )
        
        # Double-check that password was actually hashed
        if "hashed_password" not in password_validation:
            logger.error("Password validation succeeded but no hashed password generated")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing incomplete. Please try again."
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            title=user_data.title,
            phone=user_data.phone,
            hashed_password=password_validation["hashed_password"],
            role=UserRole.VIEWER,  # Default role for new registrations
            is_active=True,  # Auto-activate for now (in production, might require email verification)
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Convert to profile schema
        user_profile = UserProfile.model_validate(new_user)
        
        logger.info("User registered successfully", 
                   user_id=new_user.id, 
                   email=new_user.email)
        
        # TODO: Add background task for welcome email
        # background_tasks.add_task(send_welcome_email, new_user.email)
        
        return RegisterResponse(
            message="Account created successfully",
            user=user_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Authenticate user and return access tokens
    
    Args:
        login_data: Login credentials (email, password)
        db: Database session
        
    Returns:
        Login response with access and refresh tokens
        
    Raises:
        AuthenticationError: If credentials are invalid
    """
    try:
        # Find user by email
        user_query = select(User).where(User.email == login_data.email)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        # Check if user exists and password is correct (with fallback verification)
        if not user:
            logger.warning("Failed login attempt - user not found", email=login_data.email)
            raise AuthenticationError("Invalid email or password")
        
        # Try multiple password verification methods
        password_valid = False
        try:
            # Method 1: Try passlib verification (primary)
            password_valid = verify_password(login_data.password, user.hashed_password)
            if password_valid:
                logger.info("Primary passlib password verification succeeded")
        except Exception as e:
            logger.warning("Primary password verification failed, trying simple bcrypt", error=str(e))
            
        if not password_valid:
            try:
                # Method 2: Try simple bcrypt verification (fallback)
                password_valid = simple_verify_password(login_data.password, user.hashed_password)
                if password_valid:
                    logger.info("Simple bcrypt password verification succeeded")
            except Exception as e:
                logger.warning("Simple password verification failed", error=str(e))
        
        if not password_valid:
            logger.warning("Failed login attempt - invalid password", email=login_data.email)
            raise AuthenticationError("Invalid email or password")
        
        # Check if account is active
        if not user.is_active:
            logger.warning("Login attempt on disabled account", user_id=user.id)
            raise AuthenticationError("Account is disabled")
        
        # Update last login time
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Create token payload
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name
        }
        
        # Generate tokens
        tokens = jwt_handler.create_token_pair(token_payload)
        
        # Convert user to profile
        user_profile = UserProfile.model_validate(user)
        
        logger.info("User logged in successfully", 
                   user_id=user.id, 
                   email=user.email,
                   role=user.role.value)
        
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=user_profile
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Generate new access token from refresh token
    
    Args:
        refresh_data: Refresh token request
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        AuthenticationError: If refresh token is invalid
    """
    try:
        # Get new access token
        new_access_token = jwt_handler.refresh_access_token(refresh_data.refresh_token)
        
        if not new_access_token:
            logger.warning("Invalid refresh token")
            raise AuthenticationError("Invalid refresh token")
        
        # Get token expiration info
        settings = jwt_handler.settings
        expires_in = settings.jwt_expiration_hours * 3600
        
        logger.info("Token refreshed successfully")
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=expires_in
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user (invalidate tokens)
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        Logout success message
    """
    # TODO: Implement token blacklisting in production
    # For now, just log the logout event
    
    logger.info("User logged out", user_id=current_user.id, email=current_user.email)
    
    return {
        "message": "Successfully logged out",
        "detail": "Please discard your access and refresh tokens"
    }

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user profile
    
    Args:
        current_user: Currently authenticated user
        
    Returns:
        User profile information
    """
    logger.info("User profile requested", user_id=current_user.id)
    return UserProfile.model_validate(current_user)

@router.put("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Change user password
    
    Args:
        password_data: Current and new password
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        Password change success message
        
    Raises:
        HTTPException: If current password is wrong or new password is invalid
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            logger.warning("Password change with wrong current password", user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        password_validation = password_utils.validate_and_hash_password(password_data.new_password)
        
        if not password_validation["valid"]:
            logger.warning("Invalid new password", user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "New password does not meet security requirements",
                    "errors": password_validation["errors"]
                }
            )
        
        # Update password
        current_user.hashed_password = password_validation["hashed_password"]
        current_user.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.info("Password changed successfully", user_id=current_user.id)
        
        return {
            "message": "Password changed successfully",
            "detail": "Please login again with your new password"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change failed", user_id=current_user.id, error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.post("/reset-password")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Request password reset (send reset email)
    
    Args:
        reset_data: Email for password reset
        background_tasks: Background task handler
        db: Database session
        
    Returns:
        Password reset request confirmation
    """
    try:
        # Find user by email
        user_query = select(User).where(User.email == reset_data.email)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        # Always return success for security (don't reveal if email exists)
        message = "If the email address is registered, you will receive password reset instructions."
        
        if user and user.is_active:
            # TODO: Generate password reset token and send email
            # reset_token = generate_reset_token(user.id)
            # background_tasks.add_task(send_password_reset_email, user.email, reset_token)
            
            logger.info("Password reset requested", user_id=user.id, email=user.email)
        else:
            logger.info("Password reset requested for non-existent user", email=reset_data.email)
        
        return {
            "message": message,
            "detail": "Check your email for reset instructions"
        }
        
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        # Still return success for security
        return {
            "message": "If the email address is registered, you will receive password reset instructions."
        }

@router.get("/validate-token")
async def validate_token(
    current_user: User = Depends(get_current_user)
):
    """
    Validate if current token is valid
    
    Args:
        current_user: Currently authenticated user (validates token)
        
    Returns:
        Token validation result
    """
    logger.info("Token validated", user_id=current_user.id)
    
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value
    }