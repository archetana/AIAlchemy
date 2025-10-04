"""
Google Cloud Storage Authentication Helper
Handles service account key from environment variables for Cloud Run deployment
"""

import os
import json
import base64
import tempfile
from pathlib import Path
from typing import Optional
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

class GCSAuthManager:
    """Manages GCS authentication from various sources"""
    
    _instance = None
    _client = None
    _credentials_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._setup_authentication()
    
    def _setup_authentication(self):
        """Set up GCS authentication from available sources"""
        
        # Method 1: Base64 encoded key from environment (Cloud Run)
        if self._setup_from_base64():
            return
            
        # Method 2: Local key file (development)
        if self._setup_from_file():
            return
            
        # Method 3: Default credentials (Cloud Run with Workload Identity)
        if self._setup_default_credentials():
            return
            
        logger.warning("No GCS authentication method available")
    
    def _setup_from_base64(self) -> bool:
        """Setup from base64 encoded service account key"""
        
        encoded_key = os.getenv('GCS_SERVICE_ACCOUNT_KEY_BASE64')
        if not encoded_key:
            logger.debug("No base64 encoded GCS key found")
            return False
        
        try:
            # Decode the base64 key
            key_json = base64.b64decode(encoded_key).decode('utf-8')
            key_data = json.loads(key_json)
            
            # Create temporary file for the key
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            temp_file.write(key_json)
            temp_file.close()
            
            # Set up environment for google-cloud-storage
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name
            self._credentials_file = temp_file.name
            
            # Create client
            self._client = storage.Client()
            
            logger.info(f"GCS authenticated using base64 key for project: {key_data.get('project_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup GCS from base64 key: {e}")
            return False
    
    def _setup_from_file(self) -> bool:
        """Setup from local service account key file"""
        
        # Check common locations for the key file
        possible_paths = [
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            './gcs-service-account-key.json',
            '../gcs-service-account-key.json',
            '/app/gcs-service-account-key.json',
        ]
        
        for path in possible_paths:
            if not path:
                continue
                
            key_path = Path(path)
            if key_path.exists():
                try:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(key_path)
                    self._client = storage.Client()
                    
                    logger.info(f"GCS authenticated using key file: {key_path}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to setup GCS from file {key_path}: {e}")
                    continue
        
        logger.debug("No valid GCS key file found")
        return False
    
    def _setup_default_credentials(self) -> bool:
        """Setup using default credentials (for Cloud Run with Workload Identity)"""
        
        try:
            self._client = storage.Client()
            logger.info("GCS authenticated using default credentials")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup GCS with default credentials: {e}")
            return False
    
    def get_client(self) -> Optional[storage.Client]:
        """Get the authenticated GCS client"""
        return self._client
    
    def is_authenticated(self) -> bool:
        """Check if GCS authentication is available"""
        return self._client is not None
    
    def get_project_id(self) -> Optional[str]:
        """Get the authenticated project ID"""
        if self._client:
            return self._client.project
        return None
    
    def cleanup(self):
        """Clean up temporary files"""
        if self._credentials_file and os.path.exists(self._credentials_file):
            try:
                os.unlink(self._credentials_file)
                logger.debug(f"Cleaned up temporary credentials file: {self._credentials_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup credentials file: {e}")

# Global instance
gcs_auth = GCSAuthManager()

def get_gcs_client() -> Optional[storage.Client]:
    """Get the global GCS client instance"""
    return gcs_auth.get_client()

def is_gcs_available() -> bool:
    """Check if GCS is available and authenticated"""
    return gcs_auth.is_authenticated()

# Cleanup on module exit
import atexit
atexit.register(gcs_auth.cleanup)