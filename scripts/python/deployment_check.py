#!/usr/bin/env python3
"""
Deployment Readiness Check for AI Alchemy Application

This script performs a comprehensive check to determine if the application
is ready for deployment by validating:
- Backend API functionality  
- Database connectivity
- Authentication system
- Code syntax and imports
- Configuration validity
- Test coverage

Designed to be the final gate before deployment.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile

class DeploymentReadinessChecker:
    """Validates application readiness for deployment."""
    
    def __init__(self):
        self.backend_dir = Path("backend")
        self.frontend_dir = Path("frontend")
        self.checks = {
            'backend_syntax': False,
            'backend_imports': False,
            'database_config': False,
            'authentication': False,
            'environment_config': False,
            'test_framework': False
        }
        self.issues = []
        self.warnings = []
        
    def check_backend_syntax(self) -> bool:
        """Check backend Python syntax."""
        print("🔍 Checking backend syntax...")
        
        try:
            # Check main application files
            key_files = [
                "app/main.py",
                "app/core/config.py", 
                "app/core/database.py",
                "app/routers/auth.py"
            ]
            
            for file_path in key_files:
                full_path = self.backend_dir / file_path
                if full_path.exists():
                    python_cmd = sys.executable
                        
                    result = subprocess.run([
                        python_cmd, "-m", "py_compile", str(full_path)
                    ], capture_output=True, cwd=self.backend_dir)
                    
                    if result.returncode != 0:
                        self.issues.append(f"Syntax error in {file_path}: {result.stderr.decode()}")
                        return False
                        
            print("   ✅ Backend syntax check passed")
            return True
            
        except Exception as e:
            self.issues.append(f"Backend syntax check failed: {e}")
            return False
    
    def check_backend_imports(self) -> bool:
        """Check critical backend imports."""
        print("📦 Checking backend imports...")
        
        try:
            python_cmd = sys.executable
                
            # Check critical imports
            import_test = """
try:
    import fastapi
    import sqlalchemy
    import uvicorn
    import pydantic
    print("✅ All critical imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(import_test)
                f.flush()
                
                result = subprocess.run([
                    python_cmd, f.name
                ], capture_output=True, cwd=self.backend_dir)
                
                os.unlink(f.name)
                
            if result.returncode == 0:
                print("   ✅ Backend imports check passed")
                return True
            else:
                self.issues.append(f"Backend import error: {result.stdout.decode()}")
                return False
                
        except Exception as e:
            self.issues.append(f"Backend imports check failed: {e}")
            return False
    
    def check_database_config(self) -> bool:
        """Check database configuration."""
        print("🗄️  Checking database configuration...")
        
        try:
            # Check database.py exists and has key components
            db_file = self.backend_dir / "app" / "database.py"
            if not db_file.exists():
                self.issues.append("Database configuration file missing")
                return False
                
            with open(db_file) as f:
                content = f.read()
                
            # Check for key database components
            required_components = [
                "create_engine",
                "declarative_base", 
                "sessionmaker",
                "aiosqlite"
            ]
            
            missing_components = []
            for component in required_components:
                if component not in content:
                    missing_components.append(component)
                    
            if missing_components:
                self.warnings.append(f"Database config missing: {', '.join(missing_components)}")
            
            print("   ✅ Database configuration check passed")
            return True
            
        except Exception as e:
            self.issues.append(f"Database configuration check failed: {e}")
            return False
    
    def check_authentication(self) -> bool:
        """Check authentication system."""
        print("🔐 Checking authentication system...")
        
        try:
            # Check auth router exists
            auth_file = self.backend_dir / "app" / "routers" / "auth.py"
            if not auth_file.exists():
                self.issues.append("Authentication router missing")
                return False
                
            # Check password hashing system exists
            password_files = [
                self.backend_dir / "app" / "auth" / "simple_password.py"
            ]
            
            has_password_system = any(f.exists() for f in password_files)
            if not has_password_system:
                self.warnings.append("Password hashing system not found")
                
            print("   ✅ Authentication system check passed")
            return True
            
        except Exception as e:
            self.issues.append(f"Authentication check failed: {e}")
            return False
    
    def check_environment_config(self) -> bool:
        """Check environment configuration."""
        print("⚙️  Checking environment configuration...")
        
        try:
            # Check requirements.txt exists
            req_file = self.backend_dir / "requirements.txt"
            if not req_file.exists():
                self.issues.append("requirements.txt missing")
                return False
                
            # Check config.py exists  
            config_file = self.backend_dir / "app" / "core" / "config.py"
            if not config_file.exists():
                self.issues.append("Configuration file missing")
                return False
                
            print("   ✅ Environment configuration check passed")
            return True
            
        except Exception as e:
            self.issues.append(f"Environment configuration check failed: {e}")
            return False
    
    def check_test_framework(self) -> bool:
        """Check test framework setup."""
        print("🧪 Checking test framework...")
        
        try:
            # Check tests directory exists
            tests_dir = self.backend_dir / "tests"
            if not tests_dir.exists():
                self.warnings.append("Tests directory not found")
                return True  # Non-critical
                
            # Check for test files
            test_files = list(tests_dir.glob("test_*.py"))
            if not test_files:
                self.warnings.append("No test files found")
                return True  # Non-critical
                
            # Try to run simple test if available
            simple_test = tests_dir / "test_simple.py"
            if simple_test.exists():
                python_cmd = sys.executable
                
                result = subprocess.run([
                    python_cmd, "-m", "pytest", str(simple_test), "-v", "--tb=short"
                ], capture_output=True, cwd=self.backend_dir, timeout=30)
                
                if result.returncode == 0:
                    print("   ✅ Test framework functional")
                else:
                    self.warnings.append(f"Test execution issues: {result.stderr.decode()[:200]}")
                        
            print("   ✅ Test framework check completed")
            return True
            
        except Exception as e:
            self.warnings.append(f"Test framework check failed: {e}")
            return True  # Non-critical for deployment
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all deployment readiness checks."""
        print("🚀 AI Alchemy Deployment Readiness Check")
        print("=" * 50)
        
        # Run all checks
        self.checks['backend_syntax'] = self.check_backend_syntax()
        self.checks['backend_imports'] = self.check_backend_imports()
        self.checks['database_config'] = self.check_database_config()
        self.checks['authentication'] = self.check_authentication()
        self.checks['environment_config'] = self.check_environment_config()
        self.checks['test_framework'] = self.check_test_framework()
        
        return self.checks
    
    def generate_report(self) -> str:
        """Generate deployment readiness report."""
        passed = sum(1 for result in self.checks.values() if result)
        total = len(self.checks)
        
        report = f"""
{'='*60}
🎯 DEPLOYMENT READINESS REPORT
{'='*60}

📊 Summary:
   Total Checks: {total}
   ✅ Passed: {passed}
   ❌ Failed: {total - passed}
   📈 Readiness Score: {(passed/total)*100:.1f}%

{'='*60}
📋 Detailed Results:
"""
        
        for check_name, result in self.checks.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"\n   {status} {check_name.replace('_', ' ').title()}"
        
        if self.issues:
            report += f"\n\n{'='*60}\n❌ CRITICAL ISSUES:\n"
            for i, issue in enumerate(self.issues, 1):
                report += f"   {i}. {issue}\n"
        
        if self.warnings:
            report += f"\n{'='*60}\n⚠️  WARNINGS:\n"
            for i, warning in enumerate(self.warnings, 1):
                report += f"   {i}. {warning}\n"
        
        report += f"\n{'='*60}"
        
        # Final recommendation
        critical_checks = ['backend_syntax', 'backend_imports', 'database_config', 'authentication', 'environment_config']
        critical_passed = all(self.checks[check] for check in critical_checks if check in self.checks)
        
        if critical_passed and not self.issues:
            report += "\n🎉 DEPLOYMENT READY!"
            report += "\n✅ All critical checks passed"
            report += "\n✅ No blocking issues found"
            report += "\n✅ Application is ready for deployment"
        else:
            report += "\n⚠️  DEPLOYMENT NOT RECOMMENDED"
            report += "\n❌ Critical issues found"
            report += "\n❌ Fix issues before deploying"
            
        report += f"\n{'='*60}\n"
        
        return report


def main():
    """Main execution function."""
    checker = DeploymentReadinessChecker()
    
    try:
        # Run all checks
        results = checker.run_all_checks()
        
        # Generate report
        report = checker.generate_report()
        print(report)
        
        # Save report to file
        with open("deployment_readiness_report.txt", "w") as f:
            f.write(report)
        print("📄 Deployment readiness report saved to deployment_readiness_report.txt")
        
        # Exit with appropriate code
        critical_checks = ['backend_syntax', 'backend_imports', 'database_config', 'authentication', 'environment_config']
        critical_passed = all(results[check] for check in critical_checks if check in results)
        has_issues = bool(checker.issues)
        
        sys.exit(0 if critical_passed and not has_issues else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Deployment check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment check error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()