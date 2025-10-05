#!/usr/bin/env python3

"""
Version Increment Script for AIAlchemy (Python version)
Automatically increments patch version and updates build metadata
"""

import os
import re
import json
import sys
from datetime import datetime

VERSION_FILE_PATH = os.path.join(os.path.dirname(__file__), '../src/config/version.js')
PACKAGE_JSON_PATH = os.path.join(os.path.dirname(__file__), '../package.json')

def read_version_config():
    """Read current version configuration from version.js"""
    with open(VERSION_FILE_PATH, 'r') as f:
        content = f.read()
    
    # Extract current version numbers using regex
    major_match = re.search(r'major:\s*(\d+)', content)
    minor_match = re.search(r'minor:\s*(\d+)', content)
    patch_match = re.search(r'patch:\s*(\d+)', content)
    
    return {
        'major': int(major_match.group(1)) if major_match else 1,
        'minor': int(minor_match.group(1)) if minor_match else 0,
        'patch': int(patch_match.group(1)) if patch_match else 0
    }

def update_package_json(version):
    """Update package.json version"""
    with open(PACKAGE_JSON_PATH, 'r') as f:
        package_json = json.load(f)
    
    package_json['version'] = f"{version['major']}.{version['minor']}.{version['patch']}"
    
    with open(PACKAGE_JSON_PATH, 'w') as f:
        json.dump(package_json, f, indent=2)
        f.write('\n')
    
    print(f"✅ Updated package.json to version {package_json['version']}")

def generate_version_config(version, build_info):
    """Generate new version configuration"""
    build_number = build_info.get('build_number') or str(int(datetime.now().timestamp()))[-8:]
    commit_hash = build_info.get('commit_hash', 'unknown')
    build_date = datetime.now().isoformat()
    
    return f'''/**
 * Version Management for AIAlchemy
 * Auto-increments on each deployment
 */

// Version configuration
const VERSION_CONFIG = {{
  major: {version['major']},
  minor: {version['minor']},
  patch: {version['patch']},
  build: process.env.REACT_APP_BUILD_NUMBER || '{build_number}', // Use build number or timestamp
}};

// Generate version string
export const getVersion = () => {{
  return `${{VERSION_CONFIG.major}}.${{VERSION_CONFIG.minor}}.${{VERSION_CONFIG.patch}}.${{VERSION_CONFIG.build}}`;
}};

// App metadata
export const APP_INFO = {{
  name: 'AIAlchemy',
  fullName: 'AIAlchemy - AI Analyst for Startup Evaluation',
  version: getVersion(),
  description: 'AI-powered startup evaluation platform with automated due diligence, AI interviews, and investment memo generation',
  team: 'AIAlchemy Team',
  credits: [
    'Built with ❤️ by the AIAlchemy Team',
    'Powered by Google Cloud AI Services',
    'Document processing by Google Document AI',
    'Investment analysis by Google Gemini Pro'
  ],
  buildDate: '{build_date}',
  repository: 'https://github.com/archetana/AIAlchemy',
  license: 'MIT License',
  technologies: [
    'React 18+ with Material-UI',
    'FastAPI with Python 3.11+',
    'Google Cloud Vertex AI',
    'Document AI & Gemini Pro',
    'SQLite with SQLAlchemy',
    'Real-time processing pipeline'
  ]
}};

// Deployment tracking
export const DEPLOYMENT_INFO = {{
  environment: process.env.NODE_ENV || 'development',
  buildNumber: process.env.REACT_APP_BUILD_NUMBER || '{build_number}',
  commitHash: process.env.REACT_APP_COMMIT_HASH || '{commit_hash}',
  buildDate: process.env.REACT_APP_BUILD_DATE || '{build_date}',
  deploymentDate: new Date().toISOString()
}};

export default {{
  VERSION_CONFIG,
  APP_INFO,
  DEPLOYMENT_INFO,
  getVersion
}};'''

def increment_version(version_type='patch'):
    """Main function to increment version"""
    print('🚀 Incrementing version for AIAlchemy...\n')
    
    # Read current version
    current_version = read_version_config()
    print(f"📋 Current version: {current_version['major']}.{current_version['minor']}.{current_version['patch']}")
    
    # Increment version based on type
    new_version = current_version.copy()
    
    if version_type.lower() == 'major':
        new_version['major'] += 1
        new_version['minor'] = 0
        new_version['patch'] = 0
    elif version_type.lower() == 'minor':
        new_version['minor'] += 1
        new_version['patch'] = 0
    else:  # patch
        new_version['patch'] += 1
    
    print(f"🔢 New version: {new_version['major']}.{new_version['minor']}.{new_version['patch']}")
    
    # Get build information from environment
    build_info = {
        'build_number': os.getenv('BUILD_NUMBER') or os.getenv('GITHUB_RUN_NUMBER'),
        'commit_hash': os.getenv('COMMIT_SHA') or os.getenv('GITHUB_SHA'),
    }
    
    if build_info['commit_hash']:
        build_info['commit_hash'] = build_info['commit_hash'][:8]  # Short hash
    
    print(f"🏗️  Build number: {build_info.get('build_number', 'auto-generated')}")
    print(f"📝 Commit hash: {build_info.get('commit_hash', 'unknown')}")
    
    # Generate and write new version configuration
    new_config = generate_version_config(new_version, build_info)
    
    with open(VERSION_FILE_PATH, 'w') as f:
        f.write(new_config)
    
    print("✅ Updated version.js")
    
    # Update package.json
    update_package_json(new_version)
    
    print(f"\n🎉 Version increment complete! New version: {new_version['major']}.{new_version['minor']}.{new_version['patch']}")
    
    return new_version

if __name__ == '__main__':
    version_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    increment_version(version_type)