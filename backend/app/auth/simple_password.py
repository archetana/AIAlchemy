"""
Simple bcrypt password hashing without passlib dependency conflicts
Direct bcrypt implementation for reliable password handling
"""

import bcrypt
import re
import structlog
from typing import Dict, List

logger = structlog.get_logger()

class SimplePasswordValidator:
    """Simple password validation without passlib dependencies"""
    
    def __init__(self):
        # Password requirements
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_special = True
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def validate_password(self, password: str) -> Dict[str, any]:
        """
        Validate password against security requirements
        
        Args:
            password: Password string to validate
            
        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []
        
        # Length validation
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        # Character requirements
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_numbers and not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
        
        if self.require_special and not re.search(f"[{re.escape(self.special_chars)}]", password):
            errors.append(f"Password must contain at least one special character: {self.special_chars}")
        
        # Common password patterns to avoid
        common_patterns = [
            r"(.)\1{2,}",  # Repeated characters (aaa, 111)
            r"(?i)(password|123456|qwerty|admin)",  # Common weak passwords
            r"^(.+)\1+$",  # Repeated patterns (abcabc)
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password):
                errors.append("Password contains common patterns and is not secure")
                break
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

class SimplePasswordUtils:
    """Simple password utilities using direct bcrypt"""
    
    def __init__(self):
        self.validator = SimplePasswordValidator()
        self.rounds = 12  # bcrypt rounds
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt directly
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            hashed_str = hashed.decode('utf-8')
            logger.info("Password hashed successfully with simple bcrypt")
            return hashed_str
        except Exception as e:
            logger.error("Simple password hashing failed", error=str(e))
            raise ValueError(f"Failed to hash password: {str(e)}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash using bcrypt directly
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Handle both string and bytes inputs
            if isinstance(hashed_password, str):
                hashed_bytes = hashed_password.encode('utf-8')
            else:
                hashed_bytes = hashed_password
            
            is_valid = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_bytes)
            logger.info("Simple password verification completed", valid=is_valid)
            return is_valid
        except Exception as e:
            logger.error("Simple password verification failed", error=str(e))
            return False
    
    def validate_and_hash_password(self, password: str) -> Dict[str, any]:
        """
        Validate password requirements and hash if valid
        
        Args:
            password: Plain text password
            
        Returns:
            Dict with validation results and hashed password if valid
        """
        validation_result = self.validator.validate_password(password)
        
        if validation_result["valid"]:
            try:
                hashed_password = self.hash_password(password)
                validation_result["hashed_password"] = hashed_password
                logger.info("Password validated and hashed successfully with simple utils")
            except Exception as e:
                validation_result["valid"] = False
                validation_result["errors"] = validation_result.get("errors", [])
                validation_result["errors"].append(f"Failed to hash password: {str(e)}")
                logger.error("Simple password hashing failed after validation", error=str(e))
        
        return validation_result

# Global simple password utilities instance
simple_password_utils = SimplePasswordUtils()

# Convenience functions
def simple_hash_password(password: str) -> str:
    """Hash a password using direct bcrypt"""
    return simple_password_utils.hash_password(password)

def simple_verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using direct bcrypt"""
    return simple_password_utils.verify_password(plain_password, hashed_password)

def simple_validate_password(password: str) -> Dict[str, any]:
    """Validate password requirements"""
    return simple_password_utils.validator.validate_password(password)