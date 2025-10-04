"""
Password Hashing and Validation Utilities for AIAlchemy
Secure password handling using bcrypt with salt
"""

import re
from typing import Optional, Dict, List
from passlib.context import CryptContext
import structlog

logger = structlog.get_logger()

# Password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordValidator:
    """Password validation with security requirements"""
    
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
            "errors": errors,
            "score": self._calculate_strength_score(password)
        }
    
    def _calculate_strength_score(self, password: str) -> int:
        """
        Calculate password strength score (0-100)
        
        Args:
            password: Password string
            
        Returns:
            Strength score from 0 (weak) to 100 (very strong)
        """
        score = 0
        
        # Length scoring
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Character diversity
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 10
        if re.search(f"[{re.escape(self.special_chars)}]", password):
            score += 15
        
        # Additional complexity
        char_types = sum([
            bool(re.search(r"[a-z]", password)),
            bool(re.search(r"[A-Z]", password)),
            bool(re.search(r"\d", password)),
            bool(re.search(f"[{re.escape(self.special_chars)}]", password))
        ])
        
        if char_types >= 3:
            score += 10
        if char_types == 4:
            score += 5
        
        # Penalize common patterns
        if re.search(r"(.)\1{2,}", password):
            score -= 20
        if re.search(r"(?i)(password|123456|qwerty)", password):
            score -= 30
        
        return max(0, min(100, score))

class PasswordUtils:
    """Utility class for password hashing and verification"""
    
    def __init__(self):
        self.validator = PasswordValidator()
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            hashed = pwd_context.hash(password)
            logger.info("Password hashed successfully")
            return hashed
        except Exception as e:
            logger.error("Password hashing failed", error=str(e))
            raise ValueError("Failed to hash password")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            logger.info("Password verification completed", valid=is_valid)
            return is_valid
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
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
                logger.info("Password validated and hashed successfully")
            except Exception as e:
                validation_result["valid"] = False
                validation_result["errors"].append("Failed to hash password")
                logger.error("Password hashing failed after validation", error=str(e))
        
        return validation_result
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if password needs to be rehashed (due to algorithm updates)
        
        Args:
            hashed_password: Stored hashed password
            
        Returns:
            True if password should be rehashed
        """
        return pwd_context.needs_update(hashed_password)
    
    def generate_temporary_password(self, length: int = 12) -> str:
        """
        Generate a temporary secure password
        
        Args:
            length: Password length (default 12)
            
        Returns:
            Generated password string
        """
        import secrets
        import string
        
        # Ensure we have all character types
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ""
        
        # Add at least one of each required type
        password += secrets.choice(string.ascii_lowercase)
        password += secrets.choice(string.ascii_uppercase)
        password += secrets.choice(string.digits)
        password += secrets.choice("!@#$%^&*")
        
        # Fill the rest randomly
        for _ in range(length - 4):
            password += secrets.choice(chars)
        
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)
        
        logger.info("Temporary password generated", length=length)
        return password

# Global password utilities instance
password_utils = PasswordUtils()

# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return password_utils.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return password_utils.verify_password(plain_password, hashed_password)

def validate_password(password: str) -> Dict[str, any]:
    """Validate password requirements"""
    return password_utils.validator.validate_password(password)