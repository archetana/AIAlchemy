#!/usr/bin/env python3
"""
Test script to verify Google Cloud Storage setup for AIAlchemy
Run this after completing the GCS setup to ensure everything is working.
"""

import os
import sys
from pathlib import Path
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import tempfile

def test_gcs_setup():
    """Test Google Cloud Storage setup and configuration."""
    
    print("🧪 Testing Google Cloud Storage Setup for AIAlchemy")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. 📋 Checking Environment Variables...")
    
    required_env_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_STORAGE_BUCKET",
        "GOOGLE_APPLICATION_CREDENTIALS"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    # Check service account key file
    print("\n2. 🔑 Checking Service Account Key File...")
    
    key_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if os.path.exists(key_file):
        print(f"   ✅ Key file exists: {key_file}")
    else:
        print(f"   ❌ Key file not found: {key_file}")
        return False
    
    # Test authentication
    print("\n3. 🔐 Testing Authentication...")
    
    try:
        client = storage.Client()
        print(f"   ✅ Successfully authenticated with project: {client.project}")
    except DefaultCredentialsError as e:
        print(f"   ❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Test bucket access
    print("\n4. 🪣 Testing Bucket Access...")
    
    bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    
    try:
        bucket = client.bucket(bucket_name)
        
        # Test if bucket exists and is accessible
        if bucket.exists():
            print(f"   ✅ Bucket exists and is accessible: gs://{bucket_name}")
        else:
            print(f"   ❌ Bucket does not exist: gs://{bucket_name}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error accessing bucket: {e}")
        return False
    
    # Test write permissions
    print("\n5. ✏️ Testing Write Permissions...")
    
    try:
        test_blob_name = "test-files/aialchemy-setup-test.txt"
        test_content = "AIAlchemy GCS setup test - you can delete this file"
        
        blob = bucket.blob(test_blob_name)
        blob.upload_from_string(test_content)
        
        print(f"   ✅ Successfully uploaded test file: {test_blob_name}")
        
        # Test read permissions
        print("\n6. 📖 Testing Read Permissions...")
        
        downloaded_content = blob.download_as_text()
        if downloaded_content == test_content:
            print(f"   ✅ Successfully read test file content")
        else:
            print(f"   ⚠️ Content mismatch in test file")
        
        # Clean up test file
        blob.delete()
        print(f"   🗑️ Cleaned up test file")
        
    except Exception as e:
        print(f"   ❌ Error testing write/read permissions: {e}")
        return False
    
    # Test CORS configuration
    print("\n7. 🌐 Checking CORS Configuration...")
    
    try:
        cors = bucket.cors
        if cors:
            print(f"   ✅ CORS policy is configured ({len(cors)} rules)")
            for i, rule in enumerate(cors):
                print(f"      Rule {i+1}: Origins: {rule.get('origin', 'N/A')}, Methods: {rule.get('method', 'N/A')}")
        else:
            print(f"   ⚠️ No CORS policy found (may cause web upload issues)")
    except Exception as e:
        print(f"   ⚠️ Could not check CORS configuration: {e}")
    
    # Test lifecycle configuration
    print("\n8. ♻️ Checking Lifecycle Configuration...")
    
    try:
        lifecycle_policy = bucket.lifecycle_policy
        if lifecycle_policy.rules:
            print(f"   ✅ Lifecycle policy is configured ({len(lifecycle_policy.rules)} rules)")
            for i, rule in enumerate(lifecycle_policy.rules):
                action = rule.action
                print(f"      Rule {i+1}: {action['type']} after {rule.conditions}")
        else:
            print(f"   ⚠️ No lifecycle policy found (may increase costs)")
    except Exception as e:
        print(f"   ⚠️ Could not check lifecycle configuration: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Google Cloud Storage setup test completed successfully!")
    print("\n🎉 Your GCS configuration is ready for AIAlchemy file uploads!")
    print(f"📂 Bucket: gs://{bucket_name}")
    print(f"🔑 Service Account: Authenticated and working")
    print(f"🔐 Permissions: Read/Write access confirmed")
    
    return True

def main():
    """Main function to run GCS setup test."""
    
    # Check if running from correct directory
    if not os.path.exists("backend/app"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Load environment variables from .env file if it exists
    env_file = Path("backend/.env")
    if env_file.exists():
        print(f"📄 Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️ No .env file found in backend directory")
        print("Please ensure your GCS environment variables are set")
    
    # Run the test
    try:
        success = test_gcs_setup()
        if success:
            print("\n🚀 Ready to proceed with file upload system development!")
            sys.exit(0)
        else:
            print("\n❌ GCS setup test failed. Please fix the issues above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()