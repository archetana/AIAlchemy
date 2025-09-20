"""
Custom exception classes for AIAlchemy backend.
"""

from typing import Any, Dict, Optional
from fastapi import status


class AIAlchemyException(Exception):
    """Base exception class for AIAlchemy application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationError(AIAlchemyException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class AuthenticationError(AIAlchemyException):
    """Exception raised for authentication failures."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(AIAlchemyException):
    """Exception raised for authorization failures."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class NotFoundError(AIAlchemyException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DatabaseError(AIAlchemyException):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExternalAPIError(AIAlchemyException):
    """Exception raised for external API failures."""
    
    def __init__(self, message: str, api_name: str, status_code: int = None):
        detail = {"api_name": api_name}
        if status_code:
            detail["api_status_code"] = status_code
        
        super().__init__(
            message=f"External API error ({api_name}): {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        )


class FileProcessingError(AIAlchemyException):
    """Exception raised for file processing errors."""
    
    def __init__(self, message: str, file_type: Optional[str] = None):
        detail = {}
        if file_type:
            detail["file_type"] = file_type
        
        super().__init__(
            message=f"File processing error: {message}",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class AIServiceError(AIAlchemyException):
    """Exception raised for AI/ML service errors."""
    
    def __init__(self, message: str, service_name: str):
        super().__init__(
            message=f"AI service error ({service_name}): {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"service_name": service_name}
        )


class RateLimitError(AIAlchemyException):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )