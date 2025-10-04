#!/usr/bin/env python3
"""
Complete Google Cloud Storage Setup Script for AIAlchemy

This script helps set up Google Cloud Storage integration by:
1. Validating the current configuration
2. Providing clear instructions for missing components
3. Testing GCS connectivity when properly configured
"""

import os
import json
import sys
from pathlib import Path

def check_gcs_configuration():
    """Check current GCS configuration status"""
    print("🔍 AIAlchemy GCS Configuration Status")
    print("=" * 50)
    
    # Check backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Check .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("❌ Backend .env file not found!")
        return False
    
    print("✅ Backend directory: OK")
    print("✅ Backend .env file: OK")
    
    # Read .env configuration
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Check required environment variables
    required_vars = [
        'USE_GOOGLE_CLOUD_STORAGE',
        'GOOGLE_CLOUD_STORAGE_BUCKET',
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_CLOUD_PROJECT'
    ]
    
    print("\n📋 Environment Variables:")
    config_complete = True
    for var in required_vars:
        if var in env_vars:
            if var == 'GOOGLE_APPLICATION_CREDENTIALS':
                print(f"✅ {var}: {env_vars[var]}")
            else:
                print(f"✅ {var}: {env_vars[var]}")
        else:
            print(f"❌ {var}: Not set")
            config_complete = False
    
    # Check service account key file
    key_file = backend_dir / "gcs-service-account-key.json"
    if key_file.exists():
        print(f"✅ Service account key: {key_file}")
        try:
            with open(key_file) as f:
                key_data = json.load(f)
                print(f"   📧 Service account: {key_data.get('client_email', 'N/A')}")
                print(f"   🆔 Project ID: {key_data.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"⚠️  Key file exists but invalid: {e}")
            config_complete = False
    else:
        print(f"❌ Service account key: Missing at {key_file}")
        config_complete = False
    
    return config_complete, env_vars

def show_setup_instructions():
    """Show setup instructions for missing components"""
    print("\n🚀 GCS Setup Instructions")
    print("=" * 50)
    
    print("""
The AIAlchemy backend is configured for Google Cloud Storage, but the service
account key file is missing. Here's what you need to do:

📝 STEP 1: Generate Service Account Key
----------------------------------------
Run these commands in your terminal:

# Set your project ID (update with your actual project)
export PROJECT_ID="automatic-asset-472710-b6"

# Generate the service account key
gcloud iam service-accounts keys create ./gcs-service-account-key.json \\
    --iam-account=aialchemy-storage@$PROJECT_ID.iam.gserviceaccount.com

# Move the key to the backend directory
mv ./gcs-service-account-key.json backend/

📝 STEP 2: Verify Bucket Access
-------------------------------
# Test that your bucket exists and is accessible
gsutil ls gs://aialchemy-uploads/

# If bucket doesn't exist, create it:
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://aialchemy-uploads

📝 STEP 3: Set Up GitHub Secrets
--------------------------------
For production deployment, add these secrets to your GitHub repository:
- GCS_SERVICE_ACCOUNT_KEY (entire JSON content)
- GOOGLE_CLOUD_PROJECT (automatic-asset-472710-b6)
- GCS_BUCKET_NAME (aialchemy-uploads)
- SECRET_KEY (generate with: openssl rand -hex 32)
- JWT_SECRET_KEY (generate with: openssl rand -hex 32)

See GITHUB_SECRETS_SETUP.md for detailed instructions.

📝 STEP 4: Test Configuration
-----------------------------
After setting up the key file, run this script again to validate:
python3 setup-gcs-complete.py

📝 STEP 5: Deploy
-----------------
Copy github-actions-workflow-template.yml to .github/workflows/deploy-production.yml
and push to main branch to trigger deployment.
""")

def test_gcs_connectivity():
    """Test GCS connectivity if configuration is complete"""
    print("\n🧪 Testing GCS Connectivity")
    print("=" * 50)
    
    try:
        # Set up environment
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'backend/gcs-service-account-key.json'
        
        from google.cloud import storage
        
        # Initialize client
        client = storage.Client()
        
        # Test bucket access
        bucket_name = "aialchemy-uploads"
        bucket = client.bucket(bucket_name)
        
        # Test bucket exists
        if bucket.exists():
            print(f"✅ Bucket access: gs://{bucket_name}")
        else:
            print(f"❌ Bucket not found: gs://{bucket_name}")
            return False
        
        # Test write access by uploading a small test file
        blob = bucket.blob("test/connectivity-test.txt")
        blob.upload_from_string("AIAlchemy GCS connectivity test")
        print("✅ Write access: OK")
        
        # Test read access
        content = blob.download_as_text()
        if "AIAlchemy" in content:
            print("✅ Read access: OK")
        
        # Clean up test file
        blob.delete()
        print("✅ Delete access: OK")
        
        print("\n🎉 GCS setup is complete and working!")
        return True
        
    except ImportError:
        print("⚠️  google-cloud-storage not installed")
        print("Install with: pip install google-cloud-storage")
        return False
    except Exception as e:
        print(f"❌ GCS connectivity failed: {e}")
        return False

def main():
    """Main setup validation function"""
    print("🔧 AIAlchemy Google Cloud Storage Setup")
    print("=" * 60)
    
    # Change to webapp directory if not already there
    if Path.cwd().name != "webapp":
        webapp_dir = Path.cwd() / "webapp"
        if webapp_dir.exists():
            os.chdir(webapp_dir)
            print(f"📂 Changed to directory: {webapp_dir}")
    
    # Check configuration
    config_complete, env_vars = check_gcs_configuration()
    
    if not config_complete:
        show_setup_instructions()
        return 1
    
    # If configuration looks complete, test connectivity
    if test_gcs_connectivity():
        print("\n✨ Next Steps:")
        print("1. Set up GitHub secrets (see GITHUB_SECRETS_SETUP.md)")
        print("2. Create .github/workflows/deploy-production.yml from template")
        print("3. Push to main branch to trigger deployment")
        print("4. Build frontend upload components")
        return 0
    else:
        print("\n❌ Configuration validation failed")
        show_setup_instructions()
        return 1

if __name__ == "__main__":
    sys.exit(main())