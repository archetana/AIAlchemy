"""
File Upload Configuration for AIAlchemy
Centralizes file upload size limits and settings
"""

import os
from typing import Dict

class FileUploadConfig:
    """Configuration class for file upload settings"""
    
    # Default file size limits (100MB for all file types)
    DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
    
    # File size limits by category
    MAX_FILE_SIZES = {
        'document': int(os.getenv('MAX_DOCUMENT_SIZE', DEFAULT_MAX_FILE_SIZE)),
        'image': int(os.getenv('MAX_IMAGE_SIZE', DEFAULT_MAX_FILE_SIZE)),
        'video': int(os.getenv('MAX_VIDEO_SIZE', DEFAULT_MAX_FILE_SIZE)),
        'audio': int(os.getenv('MAX_AUDIO_SIZE', DEFAULT_MAX_FILE_SIZE)),
    }
    
    # Maximum total request size (for multiple file uploads)
    MAX_REQUEST_SIZE = int(os.getenv('MAX_REQUEST_SIZE', DEFAULT_MAX_FILE_SIZE))
    
    # Upload timeout settings
    UPLOAD_TIMEOUT = int(os.getenv('UPLOAD_TIMEOUT_SECONDS', 300))  # 5 minutes
    
    @classmethod
    def get_max_size_for_category(cls, category: str) -> int:
        """Get maximum file size for a specific category"""
        return cls.MAX_FILE_SIZES.get(category, cls.DEFAULT_MAX_FILE_SIZE)
    
    @classmethod
    def format_size_mb(cls, size_bytes: int) -> str:
        """Format bytes as MB string"""
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    
    @classmethod
    def get_size_limits_summary(cls) -> Dict[str, str]:
        """Get a summary of all size limits in human-readable format"""
        return {
            category: cls.format_size_mb(size)
            for category, size in cls.MAX_FILE_SIZES.items()
        }

# Global configuration instance
file_config = FileUploadConfig()