"""
JWT Token Handler for AIAlchemy Authentication
Handles JWT token creation, validation, and refresh functionality
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import get_settings
import structlog

logger = structlog.get_logger()

class JWTHandler:
    """JWT token handler with creation, validation and refresh capabilities"""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.jwt_secret_key
        self.algorithm = self.settings.jwt_algorithm
        self.access_token_expire_hours = self.settings.jwt_expiration_hours
        self.refresh_token_expire_days = 7  # Refresh tokens last 7 days
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a new access token
        
        Args:
            data: Token payload data (user_id, email, role, etc.)
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(hours=self.access_token_expire_hours)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info("Access token created", 
                   user_id=data.get("sub"), 
                   expires_at=expire.isoformat())
        
        return encoded_jwt
    
    def create_refresh_token(self, user_id: int) -> str:
        """
        Create a refresh token for long-term authentication
        
        Args:
            user_id: User ID to encode in token
            
        Returns:
            Encoded refresh token string
        """
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info("Refresh token created", 
                   user_id=user_id, 
                   expires_at=expire.isoformat())
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token has expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token has expired", exp=exp)
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning("Invalid JWT token", error=str(e))
            return None
    
    def extract_user_id(self, token: str) -> Optional[int]:
        """
        Extract user ID from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            User ID or None if invalid
        """
        payload = self.verify_token(token)
        if payload:
            try:
                return int(payload.get("sub"))
            except (ValueError, TypeError):
                logger.warning("Invalid user ID in token", payload=payload)
                return None
        return None
    
    def is_token_type(self, token: str, token_type: str) -> bool:
        """
        Check if token is of specified type (access/refresh)
        
        Args:
            token: JWT token string
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            True if token matches expected type
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("type") == token_type
        return False
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from valid refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if refresh token invalid
        """
        if not self.is_token_type(refresh_token, "refresh"):
            logger.warning("Invalid refresh token type")
            return None
        
        payload = self.verify_token(refresh_token)
        if payload:
            user_id = payload.get("sub")
            if user_id:
                # Create new access token with minimal payload
                new_payload = {"sub": user_id}
                return self.create_access_token(new_payload)
        
        return None
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create both access and refresh tokens
        
        Args:
            user_data: User data for token payload
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(int(user_data["sub"]))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_hours * 3600  # seconds
        }

# Global JWT handler instance
jwt_handler = JWTHandler()