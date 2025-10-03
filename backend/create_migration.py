#!/usr/bin/env python3
"""
Create Alembic migration for file upload system
Run this to generate a new migration file
"""

import os
import subprocess
import sys

def create_migration():
    """Create new migration for file upload system"""
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Generate migration
    migration_message = "add_enhanced_file_upload_support"
    
    cmd = [
        "alembic", "revision", "--autogenerate", 
        "-m", migration_message
    ]
    
    print(f"Creating migration: {migration_message}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration created successfully!")
            print(result.stdout)
        else:
            print("❌ Migration creation failed!")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error running alembic: {e}")

if __name__ == "__main__":
    create_migration()