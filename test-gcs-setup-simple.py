#!/usr/bin/env python3
"""
Simplified GCS test script for environments without google-cloud-storage package.
This validates the configuration and provides guidance for local testing.
"""

import os
import sys
from pathlib import Path

def validate_gcs_config():
    """Validate GCS configuration without requiring google-cloud-storage package."""
    
    print("🧪 AIAlchemy GCS Configuration Validation")
    print("=" * 50)
    
    # Check if running from correct directory
    if not os.path.exists("backend/app"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Load environment variables from .env file
    env_file = Path("backend/.env")
    env_vars = {}
    
    if env_file.exists():
        print(f"📄 Loading environment from: {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    env_vars[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️ No .env file found in backend directory")
        return False
    
    print("\n1. 📋 Checking Environment Variables...")
    
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_STORAGE_BUCKET", 
        "GOOGLE_APPLICATION_CREDENTIALS",
        "USE_GOOGLE_CLOUD_STORAGE"
    ]
    
    all_present = True
    for var in required_vars:
        value = env_vars.get(var, os.getenv(var))
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            all_present = False
    
    if not all_present:
        print("\n❌ Missing required environment variables")
        return False
    
    print("\n2. 🔑 Checking Service Account Key File...")
    
    key_file = env_vars.get("GOOGLE_APPLICATION_CREDENTIALS", "./gcs-service-account-key.json")
    key_path = Path("backend") / key_file if not os.path.isabs(key_file) else Path(key_file)
    
    if key_path.exists():
        print(f"   ✅ Key file exists: {key_path}")
        
        # Check if it looks like a valid JSON service account key
        try:
            import json
            with open(key_path) as f:
                key_data = json.load(f)
                
            required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
            missing_fields = [field for field in required_fields if field not in key_data]
            
            if missing_fields:
                print(f"   ⚠️ Service account key missing fields: {missing_fields}")
            else:
                print(f"   ✅ Service account key format valid")
                print(f"   📧 Service account email: {key_data.get('client_email')}")
                
        except Exception as e:
            print(f"   ⚠️ Could not validate key file format: {e}")
    else:
        print(f"   ❌ Key file not found: {key_path}")
        print(f"   📋 Expected location: backend/{key_file}")
        return False
    
    print("\n3. 🔗 Configuration Summary...")
    print(f"   Project: {env_vars.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"   Bucket: gs://{env_vars.get('GOOGLE_CLOUD_STORAGE_BUCKET')}")
    print(f"   Storage Mode: {'GCS' if env_vars.get('USE_GOOGLE_CLOUD_STORAGE') == 'true' else 'Local'}")
    
    print("\n✅ Basic configuration validation passed!")
    print("\n📋 Next Steps:")
    print("1. Run this command locally to test GCS access:")
    print(f"   gsutil ls gs://{env_vars.get('GOOGLE_CLOUD_STORAGE_BUCKET')}/")
    print("\n2. Test upload functionality:")
    print(f"   echo 'test' | gsutil cp - gs://{env_vars.get('GOOGLE_CLOUD_STORAGE_BUCKET')}/test.txt")
    print(f"   gsutil rm gs://{env_vars.get('GOOGLE_CLOUD_STORAGE_BUCKET')}/test.txt")
    print("\n3. Install required Python packages locally:")
    print("   pip install google-cloud-storage fastapi python-multipart")
    print("\n4. Run the full test script:")
    print("   python test-gcs-setup.py")
    
    return True

def main():
    """Main function."""
    try:
        success = validate_gcs_config()
        if success:
            print("\n🎉 Configuration looks good! Ready for GCS integration testing.")
            sys.exit(0)
        else:
            print("\n❌ Configuration issues found. Please fix and try again.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()