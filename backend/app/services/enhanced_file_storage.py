"""
Enhanced File Storage Service for AIAlchemy

Provides secure file upload with validation, virus scanning, and integration
with the document processing pipeline.
"""

import asyncio
import hashlib
import io
import logging
import mimetypes
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import aiofiles
from fastapi import UploadFile
from pydantic import BaseModel, Field

try:
    import pyclamd
    CLAMD_AVAILABLE = True
except ImportError:
    CLAMD_AVAILABLE = False
    pyclamd = None
    logging.getLogger(__name__).info("pyclamd not available - virus scanning disabled")

try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    storage = None
    logging.getLogger(__name__).info("Google Cloud Storage not available - using local storage only")


class FileValidationResult(BaseModel):
    """Result of file validation"""
    valid: bool
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    file_hash: str
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    virus_scan_result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StorageResult(BaseModel):
    """Result of file storage operation"""
    success: bool
    storage_path: str
    public_url: Optional[str] = None
    file_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class FileStorageConfig(BaseModel):
    """Configuration for enhanced file storage"""
    # File validation settings
    max_file_size_mb: int = 50
    allowed_mime_types: List[str] = Field(default_factory=lambda: [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'image/png',
        'image/jpeg',
        'image/tiff',
        'text/plain'
    ])
    allowed_extensions: List[str] = Field(default_factory=lambda: [
        '.pdf', '.pptx', '.ppt', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.tiff', '.txt'
    ])
    
    # Security settings
    enable_virus_scanning: bool = True
    clamd_socket_path: str = '/var/run/clamav/clamd.ctl'
    quarantine_infected_files: bool = True
    
    # Storage settings
    use_google_cloud_storage: bool = True
    gcs_bucket_name: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    local_storage_path: str = './uploads'
    enable_file_compression: bool = True
    
    # Processing settings
    generate_thumbnails: bool = False
    extract_metadata: bool = True
    calculate_checksums: bool = True


class EnhancedFileStorageService:
    """
    Enhanced file storage service with comprehensive security and validation.
    
    Features:
    - Multi-format file validation
    - Virus scanning integration
    - Google Cloud Storage support
    - Local storage fallback
    - File metadata extraction
    - Checksum calculation and verification
    - Secure temporary file handling
    """
    
    def __init__(self, config: FileStorageConfig):
        self.config = config
        self.logger = logging.getLogger("aialchemy.enhanced_file_storage")
        
        # Initialize virus scanner
        self.virus_scanner = None
        if self.config.enable_virus_scanning and CLAMD_AVAILABLE:
            self._initialize_virus_scanner()
        
        # Initialize Google Cloud Storage
        self.gcs_client = None
        self.gcs_bucket = None
        if self.config.use_google_cloud_storage and GCS_AVAILABLE:
            self._initialize_gcs()
        
        # Ensure local storage directory exists
        os.makedirs(self.config.local_storage_path, exist_ok=True)
    
    def _initialize_virus_scanner(self):
        """Initialize ClamAV virus scanner"""
        try:
            # Try socket connection first
            if os.path.exists(self.config.clamd_socket_path):
                self.virus_scanner = pyclamd.ClamdUnixSocket(self.config.clamd_socket_path)
            else:
                # Fallback to network connection
                self.virus_scanner = pyclamd.ClamdNetworkSocket()
            
            # Test connection
            if self.virus_scanner.ping():
                self.logger.info("ClamAV virus scanner initialized successfully")
            else:
                self.logger.warning("ClamAV ping failed, virus scanning disabled")
                self.virus_scanner = None
                
        except Exception as e:
            self.logger.error(f"Failed to initialize virus scanner: {e}")
            self.virus_scanner = None
    
    def _initialize_gcs(self):
        """Initialize Google Cloud Storage client"""
        try:
            if self.config.gcs_credentials_path and os.path.exists(self.config.gcs_credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.gcs_credentials_path
                )
                self.gcs_client = storage.Client(credentials=credentials)
            else:
                # Use default credentials
                self.gcs_client = storage.Client()
            
            if self.config.gcs_bucket_name:
                self.gcs_bucket = self.gcs_client.bucket(self.config.gcs_bucket_name)
                
                # Verify bucket exists
                if self.gcs_bucket.exists():
                    self.logger.info(f"Google Cloud Storage initialized: {self.config.gcs_bucket_name}")
                else:
                    self.logger.error(f"GCS bucket not found: {self.config.gcs_bucket_name}")
                    self.gcs_client = None
                    self.gcs_bucket = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Cloud Storage: {e}")
            self.gcs_client = None
            self.gcs_bucket = None
    
    async def validate_file(
        self,
        file: Union[UploadFile, BinaryIO, bytes, str],
        original_filename: Optional[str] = None
    ) -> FileValidationResult:
        """
        Comprehensive file validation including security checks.
        
        Args:
            file: File to validate (UploadFile, file object, bytes, or path)
            original_filename: Original filename for validation
            
        Returns:
            FileValidationResult with validation status and details
        """
        
        # Prepare file data
        file_data, filename, file_size = await self._prepare_file_data(file, original_filename)
        
        # Initialize validation result
        result = FileValidationResult(
            valid=True,
            filename=filename,
            original_filename=original_filename or filename,
            file_size=file_size,
            mime_type='',
            file_hash='',
            validation_errors=[],
            validation_warnings=[]
        )
        
        try:
            # 1. File size validation
            if file_size > self.config.max_file_size_mb * 1024 * 1024:
                result.validation_errors.append(
                    f"File size ({file_size} bytes) exceeds maximum allowed "
                    f"({self.config.max_file_size_mb} MB)"
                )
                result.valid = False
            
            # 2. MIME type detection and validation
            result.mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Additional MIME type detection from content
            if isinstance(file_data, bytes) and len(file_data) > 0:
                content_mime = self._detect_mime_from_content(file_data)
                if content_mime and content_mime != result.mime_type:
                    result.validation_warnings.append(
                        f"MIME type mismatch: extension suggests {result.mime_type}, "
                        f"content suggests {content_mime}"
                    )
                    result.mime_type = content_mime  # Trust content over extension
            
            if result.mime_type not in self.config.allowed_mime_types:
                result.validation_errors.append(f"File type not allowed: {result.mime_type}")
                result.valid = False
            
            # 3. File extension validation
            file_extension = Path(filename).suffix.lower()
            if file_extension not in self.config.allowed_extensions:
                result.validation_errors.append(f"File extension not allowed: {file_extension}")
                result.valid = False
            
            # 4. Calculate file hash
            if self.config.calculate_checksums:
                result.file_hash = hashlib.sha256(file_data).hexdigest()
            
            # 5. Virus scanning
            if self.config.enable_virus_scanning and self.virus_scanner:
                virus_result = await self._scan_for_viruses(file_data)
                result.virus_scan_result = virus_result
                
                if virus_result and virus_result != 'OK':
                    result.validation_errors.append(f"Virus detected: {virus_result}")
                    result.valid = False
            
            # 6. Content validation (basic)
            content_validation = self._validate_file_content(file_data, result.mime_type)
            if not content_validation['valid']:
                result.validation_errors.extend(content_validation['errors'])
                result.valid = False
            
            # 7. Extract metadata
            if self.config.extract_metadata:
                result.metadata = await self._extract_file_metadata(file_data, result.mime_type)
            
        except Exception as e:
            result.validation_errors.append(f"Validation error: {str(e)}")
            result.valid = False
            self.logger.error(f"File validation failed for {filename}: {e}")
        
        return result
    
    async def store_file(
        self,
        file: Union[UploadFile, BinaryIO, bytes, str],
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        validate_first: bool = True
    ) -> StorageResult:
        """
        Store file securely with optional validation.
        
        Args:
            file: File to store
            file_id: Custom file ID (generated if not provided)
            metadata: Additional metadata to store
            validate_first: Whether to validate file before storing
            
        Returns:
            StorageResult with storage details
        """
        
        # Generate file ID if not provided
        if not file_id:
            file_id = self._generate_file_id()
        
        # Initialize storage result
        result = StorageResult(
            success=False,
            storage_path='',
            file_id=file_id,
            metadata=metadata or {},
            errors=[]
        )
        
        try:
            # Validate file if requested
            if validate_first:
                validation_result = await self.validate_file(file)
                if not validation_result.valid:
                    result.errors.extend(validation_result.validation_errors)
                    return result
                
                # Update metadata with validation results
                result.metadata.update({
                    'validation_timestamp': datetime.now().isoformat(),
                    'file_hash': validation_result.file_hash,
                    'mime_type': validation_result.mime_type,
                    'original_filename': validation_result.original_filename,
                    'file_size': validation_result.file_size,
                    'virus_scan_result': validation_result.virus_scan_result
                })
            
            # Prepare file data
            file_data, filename, file_size = await self._prepare_file_data(file)
            
            # Store in Google Cloud Storage if available
            if self.gcs_bucket:
                storage_path, public_url = await self._store_in_gcs(
                    file_data, file_id, filename, result.metadata
                )
                result.storage_path = storage_path
                result.public_url = public_url
            else:
                # Fallback to local storage
                storage_path = await self._store_locally(
                    file_data, file_id, filename, result.metadata
                )
                result.storage_path = storage_path
            
            result.success = True
            self.logger.info(f"File stored successfully: {file_id} -> {result.storage_path}")
            
        except Exception as e:
            result.errors.append(f"Storage error: {str(e)}")
            self.logger.error(f"File storage failed for {file_id}: {e}")
        
        return result
    
    async def retrieve_file(
        self,
        file_id: str,
        storage_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Retrieve stored file content.
        
        Args:
            file_id: File identifier
            storage_path: Known storage path (optional)
            
        Returns:
            File content as bytes, or None if not found
        """
        
        try:
            # Try GCS first if available
            if self.gcs_bucket:
                blob_name = storage_path or f"uploads/{file_id}"
                blob = self.gcs_bucket.blob(blob_name)
                
                if blob.exists():
                    return blob.download_as_bytes()
            
            # Try local storage
            local_path = storage_path or os.path.join(self.config.local_storage_path, file_id)
            if os.path.exists(local_path):
                async with aiofiles.open(local_path, 'rb') as f:
                    return await f.read()
            
        except Exception as e:
            self.logger.error(f"File retrieval failed for {file_id}: {e}")
        
        return None
    
    async def delete_file(
        self,
        file_id: str,
        storage_path: Optional[str] = None
    ) -> bool:
        """
        Delete stored file.
        
        Args:
            file_id: File identifier
            storage_path: Known storage path (optional)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        
        try:
            deleted = False
            
            # Try GCS deletion
            if self.gcs_bucket:
                blob_name = storage_path or f"uploads/{file_id}"
                blob = self.gcs_bucket.blob(blob_name)
                
                if blob.exists():
                    blob.delete()
                    deleted = True
            
            # Try local storage deletion
            local_path = storage_path or os.path.join(self.config.local_storage_path, file_id)
            if os.path.exists(local_path):
                os.remove(local_path)
                deleted = True
            
            if deleted:
                self.logger.info(f"File deleted successfully: {file_id}")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"File deletion failed for {file_id}: {e}")
            return False
    
    # Helper methods
    
    async def _prepare_file_data(
        self,
        file: Union[UploadFile, BinaryIO, bytes, str],
        original_filename: Optional[str] = None
    ) -> Tuple[bytes, str, int]:
        """Prepare file data for processing"""
        
        if isinstance(file, UploadFile):
            # FastAPI UploadFile
            content = await file.read()
            filename = original_filename or file.filename or "unknown"
            file_size = len(content)
            
            # Reset file pointer for potential reuse
            await file.seek(0)
            
        elif isinstance(file, str):
            # File path
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file}")
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            filename = original_filename or file_path.name
            file_size = len(content)
            
        elif isinstance(file, bytes):
            # Raw bytes
            content = file
            filename = original_filename or "uploaded_file"
            file_size = len(content)
            
        else:
            # File object
            content = file.read()
            filename = original_filename or getattr(file, 'name', 'uploaded_file')
            file_size = len(content)
            
            # Reset file pointer
            if hasattr(file, 'seek'):
                file.seek(0)
        
        return content, filename, file_size
    
    def _detect_mime_from_content(self, content: bytes) -> Optional[str]:
        """Detect MIME type from file content magic bytes"""
        
        if len(content) < 4:
            return None
        
        # PDF
        if content[:4] == b'%PDF':
            return 'application/pdf'
        
        # PNG
        if content[:8] == b'\x89PNG\r\n\x1a\n':
            return 'image/png'
        
        # JPEG
        if content[:2] == b'\xff\xd8' and content[-2:] == b'\xff\xd9':
            return 'image/jpeg'
        
        # Microsoft Office (ZIP-based)
        if content[:2] == b'PK':
            # Could be DOCX, PPTX, etc.
            return None  # Let mimetypes handle it
        
        # Plain text (heuristic)
        try:
            content[:1024].decode('utf-8')
            return 'text/plain'
        except UnicodeDecodeError:
            pass
        
        return None
    
    def _validate_file_content(self, content: bytes, mime_type: str) -> Dict[str, Any]:
        """Basic content validation"""
        
        validation = {'valid': True, 'errors': []}
        
        try:
            # PDF validation
            if mime_type == 'application/pdf':
                if not content.startswith(b'%PDF'):
                    validation['valid'] = False
                    validation['errors'].append("Invalid PDF format")
            
            # Image validation
            elif mime_type.startswith('image/'):
                if mime_type == 'image/png' and not content.startswith(b'\x89PNG'):
                    validation['valid'] = False
                    validation['errors'].append("Invalid PNG format")
                
                elif mime_type == 'image/jpeg' and not content.startswith(b'\xff\xd8'):
                    validation['valid'] = False
                    validation['errors'].append("Invalid JPEG format")
            
            # Basic size check
            if len(content) == 0:
                validation['valid'] = False
                validation['errors'].append("Empty file")
            
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Content validation error: {str(e)}")
        
        return validation
    
    async def _scan_for_viruses(self, content: bytes) -> Optional[str]:
        """Scan file content for viruses"""
        
        if not self.virus_scanner:
            return None
        
        try:
            # Create temporary file for scanning
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                
                # Scan the file
                scan_result = self.virus_scanner.scan_file(temp_file.name)
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                if scan_result:
                    # Virus found
                    filename, status = list(scan_result.items())[0]
                    return status
                else:
                    # No virus found
                    return 'OK'
                    
        except Exception as e:
            self.logger.error(f"Virus scanning failed: {e}")
            return f"Scan error: {str(e)}"
    
    async def _extract_file_metadata(self, content: bytes, mime_type: str) -> Dict[str, Any]:
        """Extract file metadata"""
        
        metadata = {
            'extraction_timestamp': datetime.now().isoformat(),
            'content_length': len(content)
        }
        
        try:
            # PDF metadata
            if mime_type == 'application/pdf':
                # Would implement PDF metadata extraction
                metadata['type'] = 'pdf_document'
                
            # Image metadata
            elif mime_type.startswith('image/'):
                # Would implement image metadata extraction (EXIF, etc.)
                metadata['type'] = 'image'
                
            # Office document metadata
            elif 'officedocument' in mime_type or 'ms-' in mime_type:
                metadata['type'] = 'office_document'
                
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    async def _store_in_gcs(
        self,
        content: bytes,
        file_id: str,
        filename: str,
        metadata: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """Store file in Google Cloud Storage"""
        
        blob_name = f"uploads/{file_id}/{filename}"
        blob = self.gcs_bucket.blob(blob_name)
        
        # Set metadata
        blob.metadata = {k: str(v) for k, v in metadata.items()}
        
        # Upload content
        blob.upload_from_string(content, content_type=metadata.get('mime_type'))
        
        # Generate public URL if bucket is public
        public_url = None
        try:
            # Make blob publicly readable (optional)
            # blob.make_public()
            # public_url = blob.public_url
            pass
        except Exception as e:
            self.logger.warning(f"Could not make blob public: {e}")
        
        return blob_name, public_url
    
    async def _store_locally(
        self,
        content: bytes,
        file_id: str,
        filename: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Store file in local storage"""
        
        # Create directory structure
        file_dir = os.path.join(self.config.local_storage_path, file_id)
        os.makedirs(file_dir, exist_ok=True)
        
        # Store file
        file_path = os.path.join(file_dir, filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Store metadata
        metadata_path = os.path.join(file_dir, 'metadata.json')
        async with aiofiles.open(metadata_path, 'w') as f:
            import json
            await f.write(json.dumps(metadata, indent=2))
        
        return file_path
    
    def _generate_file_id(self) -> str:
        """Generate unique file ID"""
        import uuid
        return f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage service statistics"""
        
        stats = {
            'service_status': 'active',
            'gcs_available': self.gcs_bucket is not None,
            'virus_scanner_available': self.virus_scanner is not None,
            'local_storage_path': self.config.local_storage_path,
            'config': {
                'max_file_size_mb': self.config.max_file_size_mb,
                'allowed_mime_types': len(self.config.allowed_mime_types),
                'virus_scanning_enabled': self.config.enable_virus_scanning
            }
        }
        
        # Local storage stats
        if os.path.exists(self.config.local_storage_path):
            try:
                local_files = list(Path(self.config.local_storage_path).rglob('*'))
                stats['local_storage'] = {
                    'total_files': len([f for f in local_files if f.is_file()]),
                    'total_dirs': len([d for d in local_files if d.is_dir()])
                }
            except Exception as e:
                stats['local_storage'] = {'error': str(e)}
        
        return stats