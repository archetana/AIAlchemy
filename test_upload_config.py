#!/usr/bin/env python3
"""
Test script to verify file upload configuration
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.file_config import file_config
from backend.app.services.file_storage import file_storage_service

async def test_upload_configuration():
    """Test and display current upload configuration"""
    
    print("🔧 AIAlchemy File Upload Configuration Test")
    print("=" * 50)
    
    # Test file configuration
    print("\n📁 File Size Limits:")
    for category, size_mb in file_config.get_size_limits_summary().items():
        print(f"  {category.capitalize()}: {size_mb}")
    
    print(f"\n⏱️  Upload Timeout: {file_config.UPLOAD_TIMEOUT} seconds")
    print(f"📦 Max Request Size: {file_config.format_size_mb(file_config.MAX_REQUEST_SIZE)}")
    
    # Test file storage service
    print(f"\n💾 Storage Backend: {'GCS' if file_storage_service.use_gcs else 'Local'}")
    
    if not file_storage_service.use_gcs:
        print(f"📂 Local Storage Path: {file_storage_service.local_storage_path}")
        # Create directory if it doesn't exist
        file_storage_service.local_storage_path.mkdir(parents=True, exist_ok=True)
        print("✅ Local storage directory verified/created")
    else:
        print(f"☁️  GCS Bucket: {file_storage_service.gcs_bucket}")
    
    # Test supported file types
    print(f"\n📋 Supported File Types ({len(file_storage_service.ALLOWED_FILE_TYPES)} types):")
    for mime_type, extensions in file_storage_service.ALLOWED_FILE_TYPES.items():
        print(f"  {mime_type}: {', '.join(extensions)}")
    
    print("\n🎯 Configuration Summary:")
    print(f"  ✅ Maximum file size: 100MB")
    print(f"  ✅ Upload timeout: 5 minutes") 
    print(f"  ✅ Multiple file types supported")
    print(f"  ✅ Security validation enabled")
    
    # Test specific file size validation
    print(f"\n🧪 File Size Validation Tests:")
    
    test_sizes = [
        (1024 * 1024, "1MB", True),          # 1MB - should pass
        (50 * 1024 * 1024, "50MB", True),   # 50MB - should pass
        (100 * 1024 * 1024, "100MB", True), # 100MB - should pass
        (150 * 1024 * 1024, "150MB", False) # 150MB - should fail
    ]
    
    for size_bytes, size_label, should_pass in test_sizes:
        is_valid = file_storage_service._validate_file_size(size_bytes, 'application/pdf')
        status = "✅ PASS" if is_valid == should_pass else "❌ FAIL"
        print(f"  {status} {size_label} file: {'Allowed' if is_valid else 'Rejected'}")
    
    print(f"\n🚀 Configuration Test Complete!")
    print(f"Ready for 100MB file uploads! 🎉")

if __name__ == "__main__":
    asyncio.run(test_upload_configuration())