#!/usr/bin/env python3
"""
GitHub Actions Workflow Validation Script
Validates YAML syntax and workflow configuration
"""

import os
import yaml
from pathlib import Path

def validate_workflow_file(workflow_path):
    """Validate a single workflow file"""
    print(f"\n🔍 Validating {workflow_path.name}...")
    
    try:
        with open(workflow_path, 'r') as f:
            content = yaml.safe_load(f)
        
        # Basic validation checks
        if 'name' not in content:
            print(f"⚠️  Warning: No 'name' field in {workflow_path.name}")
        
        # Handle YAML parsing of 'on' keyword (gets parsed as boolean True)
        triggers_key = None
        if 'on' in content:
            triggers_key = 'on'
        elif True in content:  # 'on' gets parsed as boolean True
            triggers_key = True
        
        if triggers_key is None:
            print(f"❌ Error: No 'on' triggers defined in {workflow_path.name}")
            return False
        
        if 'jobs' not in content:
            print(f"❌ Error: No 'jobs' defined in {workflow_path.name}")
            return False
        
        jobs_count = len(content['jobs'])
        triggers = content[triggers_key]
        
        print(f"✅ YAML syntax valid")
        print(f"📋 Found {jobs_count} job(s)")
        print(f"⚡ Triggers: {list(triggers.keys()) if isinstance(triggers, dict) else triggers}")
        
        # Check for common issues
        if isinstance(triggers, dict) and 'push' in triggers:
            branches = triggers['push'].get('branches', [])
            if branches:
                print(f"📂 Push branches: {branches}")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def check_workflow_conflicts():
    """Check for potential workflow conflicts"""
    print(f"\n🔍 Checking for workflow conflicts...")
    
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print(f"❌ No .github/workflows directory found")
        return False
    
    workflows = {}
    
    for workflow_file in workflow_dir.glob("*.yml"):
        try:
            with open(workflow_file, 'r') as f:
                content = yaml.safe_load(f)
            
            # Handle YAML parsing of 'on' keyword 
            triggers = content.get('on', content.get(True, {}))
            workflows[workflow_file.name] = triggers
        except Exception as e:
            print(f"⚠️  Could not analyze {workflow_file.name}: {e}")
    
    # Check for overlapping triggers
    main_triggers = []
    for filename, triggers in workflows.items():
        if isinstance(triggers, dict) and 'push' in triggers:
            branches = triggers['push'].get('branches', [])
            if 'main' in branches:
                main_triggers.append(filename)
    
    if len(main_triggers) > 1:
        print(f"⚠️  Multiple workflows trigger on 'main' branch: {main_triggers}")
        print(f"   This could cause conflicts!")
    else:
        print(f"✅ No conflicting main branch triggers found")
    
    return True

def main():
    """Main validation function"""
    print("🚀 GitHub Actions Workflow Validation")
    print("=" * 50)
    
    # Change to webapp directory
    os.chdir("/home/agenticai/webapp")
    
    workflow_dir = Path(".github/workflows")
    
    if not workflow_dir.exists():
        print(f"❌ No .github/workflows directory found")
        return 1
    
    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
    
    if not workflow_files:
        print(f"❌ No workflow files found in {workflow_dir}")
        return 1
    
    print(f"📁 Found {len(workflow_files)} workflow file(s)")
    
    all_valid = True
    
    # Validate each workflow file
    for workflow_file in workflow_files:
        if not validate_workflow_file(workflow_file):
            all_valid = False
    
    # Check for conflicts
    check_workflow_conflicts()
    
    print(f"\n📋 Validation Summary")
    print("=" * 50)
    
    if all_valid:
        print(f"✅ All workflow files are valid!")
        print(f"🎉 No YAML syntax errors found")
        print(f"🚀 Workflows are ready for use")
        
        print(f"\n💡 Expected behavior:")
        print(f"   - comprehensive-tests.yml: Runs on genspark_ai_developer pushes and PRs")
        print(f"   - deploy.yml: Runs on main branch pushes (full deployment)")
        
    else:
        print(f"❌ Some workflow files have issues")
        print(f"🔧 Fix the errors above before using workflows")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    exit(main())