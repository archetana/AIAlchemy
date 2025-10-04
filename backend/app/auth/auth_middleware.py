"""
Authentication Middleware for AIAlchemy
Handles request authentication, logging, and security headers
"""

import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling authentication, logging, and security
    """
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        # Paths that don't require authentication
        self.exclude_paths = exclude_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through authentication middleware
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response object
        """
        start_time = time.time()
        
        # Extract request info for logging
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            "Request started",
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        # Add security headers to all responses
        try:
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Add CORS headers if needed (FastAPI CORS middleware should handle this)
            if method == "OPTIONS":
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            
            # Log successful request
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                method=method,
                path=path,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
                client_ip=client_ip
            )
            
            return response
            
        except Exception as e:
            # Log error and return generic error response
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                method=method,
                path=path,
                error=str(e),
                process_time_ms=round(process_time * 1000, 2),
                client_ip=client_ip
            )
            
            # Return generic error response for security
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_id": f"{int(time.time())}-{hash(str(e)) % 10000}"
                },
                headers={
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block"
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address string
        """
        # Check for IP in various headers (reverse proxy scenarios)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    """
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Apply rate limiting to requests
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response object or rate limit error
        """
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_requests(current_time)
        
        # Check rate limit
        if client_ip in self.requests:
            request_times = self.requests[client_ip]
            recent_requests = [t for t in request_times if current_time - t < self.window_seconds]
            
            if len(recent_requests) >= self.max_requests:
                logger.warning(
                    "Rate limit exceeded",
                    client_ip=client_ip,
                    requests=len(recent_requests),
                    max_requests=self.max_requests
                )
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests",
                        "retry_after": self.window_seconds
                    },
                    headers={"Retry-After": str(self.window_seconds)}
                )
        
        # Record this request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove old request records to prevent memory buildup"""
        cutoff_time = current_time - self.window_seconds
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] 
                if t > cutoff_time
            ]
            # Remove empty entries
            if not self.requests[client_ip]:
                del self.requests[client_ip]

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response