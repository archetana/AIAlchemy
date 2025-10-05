#!/usr/bin/env python3
"""
About Dialog Validation Script
Validates React components and identifies potential issues
"""

import os
import re
import sys
from pathlib import Path

def check_file_exists(file_path):
    """Check if file exists and is readable"""
    try:
        return Path(file_path).exists()
    except Exception as e:
        print(f"Error checking file {file_path}: {e}")
        return False

def analyze_imports(file_content, file_path):
    """Analyze import statements for potential issues"""
    issues = []
    
    # Find import statements
    import_pattern = r"import\s+.*?from\s+['\"](.+?)['\"]"
    imports = re.findall(import_pattern, file_content)
    
    for imp in imports:
        # Check for relative imports
        if imp.startswith('.'):
            # Resolve relative path
            base_dir = Path(file_path).parent
            resolved_path = base_dir / imp.replace('./', '').replace('../', '../')
            
            # Check different possible extensions
            possible_files = [
                f"{resolved_path}.js",
                f"{resolved_path}/index.js",
                f"{resolved_path}.jsx"
            ]
            
            found = False
            for pf in possible_files:
                if check_file_exists(pf):
                    found = True
                    break
            
            if not found:
                issues.append(f"Missing import file: {imp} (checked: {possible_files})")
    
    return issues

def check_react_syntax(file_content, file_path):
    """Check for common React/JS syntax issues"""
    issues = []
    
    # Check for process.env usage (might not be available in all contexts)
    if 'process.env' in file_content:
        issues.append("Uses process.env - ensure environment variables are available")
    
    # Check for circular references in exports/imports
    if file_path.endswith('version.js'):
        if 'get version()' in file_content and 'getVersion()' in file_content:
            issues.append("Potential circular reference in version getter")
    
    # Check for missing error handling
    if 'require(' in file_content and 'try' not in file_content:
        issues.append("Dynamic require without error handling")
    
    return issues

def validate_about_components():
    """Validate all About dialog components"""
    base_path = Path("frontend/src/components/About")
    
    if not base_path.exists():
        print(f"❌ About components directory not found: {base_path}")
        return False
    
    components = [
        "AboutDialog.js",
        "SimpleAboutDialog.js", 
        "RobustAboutDialog.js",
        "index.js"
    ]
    
    print("🔍 Validating About Dialog Components...")
    print("=" * 50)
    
    all_valid = True
    
    for component in components:
        component_path = base_path / component
        print(f"\n📄 Checking {component}...")
        
        if not check_file_exists(component_path):
            print(f"❌ File not found: {component_path}")
            all_valid = False
            continue
        
        try:
            with open(component_path, 'r') as f:
                content = f.read()
            
            print(f"✅ File exists and readable")
            print(f"📊 Size: {len(content)} characters")
            
            # Analyze imports
            import_issues = analyze_imports(content, str(component_path))
            if import_issues:
                print("⚠️  Import Issues:")
                for issue in import_issues:
                    print(f"   - {issue}")
                all_valid = False
            else:
                print("✅ All imports appear valid")
            
            # Check React syntax
            syntax_issues = check_react_syntax(content, str(component_path))
            if syntax_issues:
                print("⚠️  Syntax/Logic Issues:")
                for issue in syntax_issues:
                    print(f"   - {issue}")
            else:
                print("✅ No syntax issues detected")
        
        except Exception as e:
            print(f"❌ Error reading {component}: {e}")
            all_valid = False
    
    return all_valid

def validate_version_config():
    """Validate version configuration"""
    version_path = Path("frontend/src/config/version.js")
    
    print(f"\n🔧 Validating Version Configuration...")
    print("=" * 50)
    
    if not check_file_exists(version_path):
        print(f"❌ Version config not found: {version_path}")
        return False
    
    try:
        with open(version_path, 'r') as f:
            content = f.read()
        
        print(f"✅ Version config exists")
        
        # Check for potential issues
        issues = []
        
        if 'process.env' in content and 'try' not in content:
            issues.append("process.env used without error handling")
        
        if content.count('getVersion') > 2:
            issues.append("Multiple getVersion references - check for circular references")
        
        if 'export' in content and 'module.exports' in content:
            issues.append("Mixed ES6 and CommonJS export syntax")
        
        if issues:
            print("⚠️  Potential Issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Version config looks good")
            return True
    
    except Exception as e:
        print(f"❌ Error reading version config: {e}")
        return False

def validate_navigation_component():
    """Validate TopNavigation component"""
    nav_path = Path("frontend/src/components/Navigation/TopNavigation.js")
    
    print(f"\n🧭 Validating Navigation Component...")
    print("=" * 50)
    
    if not check_file_exists(nav_path):
        print(f"❌ Navigation component not found: {nav_path}")
        return False
    
    try:
        with open(nav_path, 'r') as f:
            content = f.read()
        
        print(f"✅ Navigation component exists")
        
        # Check for About dialog integration
        if 'AboutDialog' in content or 'RobustAboutDialog' in content:
            print("✅ About dialog import found")
        else:
            print("❌ No About dialog import found")
            return False
        
        if 'handleAboutClick' in content:
            print("✅ About click handler found")
        else:
            print("❌ About click handler missing")
            return False
        
        if 'aboutDialogOpen' in content:
            print("✅ About dialog state management found")
        else:
            print("❌ About dialog state management missing")
            return False
        
        # Check for menu item
        if 'About' in content and 'MenuItem' in content:
            print("✅ About menu item found")
        else:
            print("⚠️  About menu item might be missing")
        
        return True
    
    except Exception as e:
        print(f"❌ Error reading navigation component: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 AIAlchemy About Dialog Validation")
    print("=" * 50)
    
    # Change to webapp directory
    os.chdir("/home/agenticai/webapp")
    
    results = {
        'about_components': validate_about_components(),
        'version_config': validate_version_config(),
        'navigation': validate_navigation_component()
    }
    
    print(f"\n📋 Validation Summary")
    print("=" * 50)
    
    for component, valid in results.items():
        status = "✅ PASS" if valid else "❌ FAIL"
        print(f"{component.replace('_', ' ').title()}: {status}")
    
    all_valid = all(results.values())
    
    if all_valid:
        print(f"\n🎉 All validations passed! The About dialog should be working.")
        print(f"\n💡 If the About dialog is still not visible, the issue might be:")
        print(f"   - Frontend build/compilation errors")
        print(f"   - Runtime JavaScript errors in the browser")
        print(f"   - CSS/styling issues hiding the dialog")
        print(f"   - React component lifecycle issues")
        
        print(f"\n🔧 Next steps to debug:")
        print(f"   1. Check browser console for JavaScript errors")
        print(f"   2. Verify the React app compiles and runs")
        print(f"   3. Use React DevTools to inspect component state")
        print(f"   4. Check if the AboutDialog component renders in DOM")
    else:
        print(f"\n❌ Some validations failed. Fix the issues above first.")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())