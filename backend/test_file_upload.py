#!/usr/bin/env python3
"""
Test script for file upload functionality
"""

import asyncio
import tempfile
import os
from pathlib import Path
from fastapi import UploadFile
from io import BytesIO

async def test_file_upload():
    """Test the file upload service"""
    
    try:
        from app.services.file_storage import file_storage_service
        
        # Create a test file
        test_content = b"This is a test PDF document content for AIAlchemy file upload testing."
        test_filename = "test_pitch_deck.pdf"
        
        # Create a mock UploadFile
        class MockUploadFile:
            def __init__(self, filename, content, content_type):
                self.filename = filename
                self.content = content
                self.content_type = content_type
                self._file = BytesIO(content)
            
            async def read(self):
                return self.content
        
        mock_file = MockUploadFile(
            filename=test_filename,
            content=test_content, 
            content_type="application/pdf"
        )
        
        print("🧪 Testing file upload service...")
        
        # Test upload
        result = await file_storage_service.upload_file(
            file=mock_file,
            startup_id=1,
            file_type="pitch_deck",
            description="Test pitch deck upload"
        )
        
        print("✅ Upload successful!")
        print(f"File ID: {result['file_id']}")
        print(f"Storage path: {result['storage_path']}")
        print(f"File size: {result['file_size']} bytes")
        print(f"File hash: {result['file_hash']}")
        
        # Test file retrieval
        print("\n🔍 Testing file retrieval...")
        file_content = await file_storage_service.get_file(result['storage_path'])
        
        if file_content == test_content:
            print("✅ File retrieval successful!")
        else:
            print("❌ File content mismatch!")
        
        # Test file deletion
        print("\n🗑️  Testing file deletion...")
        deleted = await file_storage_service.delete_file(result['storage_path'])
        
        if deleted:
            print("✅ File deletion successful!")
        else:
            print("❌ File deletion failed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_file_validation():
    """Test file validation logic"""
    
    try:
        from app.services.file_storage import file_storage_service
        
        print("\n📋 Testing file validation...")
        
        # Test allowed file type
        valid = file_storage_service._validate_file_type("test.pdf", "application/pdf")
        print(f"PDF validation: {'✅ Pass' if valid else '❌ Fail'}")
        
        # Test disallowed file type
        invalid = file_storage_service._validate_file_type("test.exe", "application/octet-stream")
        print(f"EXE validation: {'✅ Pass (correctly rejected)' if not invalid else '❌ Fail (should be rejected)'}")
        
        # Test file size validation
        size_ok = file_storage_service._validate_file_size(1024 * 1024, "application/pdf")  # 1MB
        print(f"Size validation (1MB PDF): {'✅ Pass' if size_ok else '❌ Fail'}")
        
        size_too_big = file_storage_service._validate_file_size(100 * 1024 * 1024, "application/pdf")  # 100MB
        print(f"Size validation (100MB PDF): {'✅ Pass (correctly rejected)' if not size_too_big else '❌ Fail (should be rejected)'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running file upload tests...\n")
    
    async def run_tests():
        test1 = await test_file_upload()
        test2 = await test_file_validation()
        
        if test1 and test2:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    
    asyncio.run(run_tests())