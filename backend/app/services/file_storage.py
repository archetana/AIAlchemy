"""
File Storage Service for AIAlchemy
Handles file uploads, validation, and storage (local/GCS)
"""

import os
import uuid
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any
import aiofiles
from fastapi import UploadFile, HTTPException
from datetime import datetime
import hashlib
import logging

from ..core.config import get_settings
from ..core.gcs_auth import get_gcs_client, is_gcs_available

logger = logging.getLogger(__name__)

class FileStorageService:
    """Handles file upload and storage operations"""
    
    # Supported file types and their MIME types
    ALLOWED_FILE_TYPES = {
        # Documents
        'application/pdf': ['.pdf'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'application/msword': ['.doc'],
        'application/vnd.ms-powerpoint': ['.ppt'],
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
        'text/plain': ['.txt'],
        'text/csv': ['.csv'],
        
        # Images
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        
        # Videos
        'video/mp4': ['.mp4'],
        'video/quicktime': ['.mov'],
        'video/x-msvideo': ['.avi'],
        
        # Audio
        'audio/mpeg': ['.mp3'],
        'audio/wav': ['.wav'],
        'audio/mp4': ['.m4a'],
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'document': 50 * 1024 * 1024,  # 50MB for documents
        'image': 10 * 1024 * 1024,     # 10MB for images
        'video': 500 * 1024 * 1024,    # 500MB for videos
        'audio': 100 * 1024 * 1024,    # 100MB for audio
    }
    
    def __init__(self):
        """Initialize file storage service"""
        self.use_gcs = os.getenv('USE_GOOGLE_CLOUD_STORAGE', 'false').lower() == 'true'
        self.gcs_bucket = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET', 'aialchemy-uploads')
        self.local_storage_path = Path(os.getenv('LOCAL_UPLOAD_PATH', './uploads'))
        
        # Create local storage directory if it doesn't exist
        if not self.use_gcs:
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_category(self, mime_type: str) -> str:
        """Determine file category based on MIME type"""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        else:
            return 'document'
    
    def _validate_file_type(self, filename: str, content_type: str) -> bool:
        """Validate file type based on extension and MIME type"""
        file_ext = Path(filename).suffix.lower()
        
        # Check if MIME type is allowed
        if content_type not in self.ALLOWED_FILE_TYPES:
            return False
        
        # Check if extension matches MIME type
        allowed_extensions = self.ALLOWED_FILE_TYPES[content_type]
        return file_ext in allowed_extensions
    
    def _validate_file_size(self, file_size: int, content_type: str) -> bool:
        """Validate file size based on category"""
        category = self._get_file_category(content_type)
        max_size = self.MAX_FILE_SIZES.get(category, self.MAX_FILE_SIZES['document'])
        return file_size <= max_size
    
    async def _scan_file_content(self, file_path: Path) -> Dict[str, Any]:
        """Basic file content validation (placeholder for virus scanning)"""
        # TODO: Implement actual virus scanning with ClamAV or similar
        # For now, just check file size and basic properties
        
        try:
            stat = file_path.stat()
            return {
                'is_safe': True,
                'file_size': stat.st_size,
                'scan_result': 'clean',
                'scan_timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'is_safe': False,
                'file_size': 0,
                'scan_result': f'scan_error: {str(e)}',
                'scan_timestamp': datetime.utcnow().isoformat()
            }
    
    def _generate_file_hash(self, content: bytes) -> str:
        """Generate SHA-256 hash of file content for deduplication"""
        return hashlib.sha256(content).hexdigest()
    
    async def upload_file(
        self, 
        file: UploadFile, 
        startup_id: int,
        file_type: str = 'document',
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload and store a file
        
        Args:
            file: FastAPI UploadFile object
            startup_id: ID of the startup this file belongs to
            file_type: Type of file (pitch_deck, financial_docs, etc.)
            description: Optional description of the file
            
        Returns:
            Dict with file metadata and storage info
        """
        
        # Validate file type
        if not self._validate_file_type(file.filename, file.content_type):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported types: {list(self.ALLOWED_FILE_TYPES.keys())}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if not self._validate_file_size(file_size, file.content_type):
            category = self._get_file_category(file.content_type)
            max_size_mb = self.MAX_FILE_SIZES[category] / (1024 * 1024)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size for {category} files: {max_size_mb}MB"
            )
        
        # Generate unique file ID and hash
        file_id = str(uuid.uuid4())
        file_hash = self._generate_file_hash(content)
        
        # Determine file extension
        file_ext = Path(file.filename).suffix.lower()
        stored_filename = f"{file_id}{file_ext}"
        
        # Storage path structure: startup_id/file_type/filename
        relative_path = f"{startup_id}/{file_type}/{stored_filename}"
        
        if self.use_gcs:
            # Upload to Google Cloud Storage
            storage_path = await self._upload_to_gcs(content, relative_path)
        else:
            # Store locally
            storage_path = await self._upload_to_local(content, relative_path)
        
        # Scan file for security
        if not self.use_gcs:
            scan_result = await self._scan_file_content(Path(storage_path))
        else:
            # For GCS, we'd implement cloud-based scanning
            scan_result = {'is_safe': True, 'scan_result': 'gcs_pending'}
        
        # Return file metadata
        return {
            'file_id': file_id,
            'original_filename': file.filename,
            'stored_filename': stored_filename,
            'content_type': file.content_type,
            'file_size': file_size,
            'file_hash': file_hash,
            'file_type': file_type,
            'startup_id': startup_id,
            'description': description,
            'storage_path': storage_path,
            'relative_path': relative_path,
            'upload_timestamp': datetime.utcnow().isoformat(),
            'is_safe': scan_result['is_safe'],
            'scan_result': scan_result,
            'storage_backend': 'gcs' if self.use_gcs else 'local'
        }
    
    async def _upload_to_local(self, content: bytes, relative_path: str) -> str:
        """Upload file to local storage"""
        full_path = self.local_storage_path / relative_path
        
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(content)
        
        return str(full_path)
    
    async def _upload_to_gcs(self, content: bytes, relative_path: str) -> str:
        """Upload file to Google Cloud Storage"""
        # NOTE: This requires google-cloud-storage package
        # Implementation will be added after GCS setup
        
        try:
            from google.cloud import storage
            
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)
            blob = bucket.blob(relative_path)
            
            # Upload content
            blob.upload_from_string(content)
            
            return f"gs://{self.gcs_bucket}/{relative_path}"
        
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="Google Cloud Storage not configured. Install google-cloud-storage package."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload to Google Cloud Storage: {str(e)}"
            )
    
    async def get_file(self, file_path: str) -> bytes:
        """Retrieve file content"""
        if file_path.startswith('gs://'):
            return await self._get_file_from_gcs(file_path)
        else:
            return await self._get_file_from_local(file_path)
    
    async def _get_file_from_local(self, file_path: str) -> bytes:
        """Get file from local storage"""
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
    
    async def _get_file_from_gcs(self, file_path: str) -> bytes:
        """Get file from Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            # Parse GCS path: gs://bucket/path
            parts = file_path.replace('gs://', '').split('/', 1)
            bucket_name, blob_name = parts[0], parts[1]
            
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            return blob.download_as_bytes()
        
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"File not found in Google Cloud Storage: {str(e)}"
            )
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        if file_path.startswith('gs://'):
            return await self._delete_file_from_gcs(file_path)
        else:
            return await self._delete_file_from_local(file_path)
    
    async def _delete_file_from_local(self, file_path: str) -> bool:
        """Delete file from local storage"""
        try:
            Path(file_path).unlink()
            return True
        except FileNotFoundError:
            return False
    
    async def _delete_file_from_gcs(self, file_path: str) -> bool:
        """Delete file from Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            # Parse GCS path
            parts = file_path.replace('gs://', '').split('/', 1)
            bucket_name, blob_name = parts[0], parts[1]
            
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            
            return True
        except Exception:
            return False

# Global instance
file_storage_service = FileStorageService()