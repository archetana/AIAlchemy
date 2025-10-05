#!/usr/bin/env python3
"""
Comprehensive test runner for the FastAPI application.

This script runs all tests in headless mode to verify correctness before deployment.
It provides detailed reporting and can be integrated into CI/CD pipelines.
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import shutil

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

class TestRunner:
    """Comprehensive test runner with detailed reporting."""
    
    def __init__(self):
        self.test_results: Dict[str, bool] = {}
        self.test_outputs: Dict[str, str] = {}
        self.temp_db_path = None
        
    def setup_test_environment(self):
        """Set up isolated test environment."""
        print("🔧 Setting up test environment...")
        
        # Create temporary database file
        temp_dir = tempfile.mkdtemp()
        self.temp_db_path = os.path.join(temp_dir, "test.db")
        
        # Set test environment variables
        os.environ.update({
            'ENVIRONMENT': 'test',
            'DATABASE_URL': f'sqlite+aiosqlite:///{self.temp_db_path}',
            'JWT_SECRET_KEY': 'test-secret-key-for-testing-only',
            'JWT_ALGORITHM': 'HS256',
            'JWT_ACCESS_TOKEN_EXPIRE_MINUTES': '30'
        })
        
        print(f"✅ Test database: {self.temp_db_path}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_db_path and os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
                os.rmdir(os.path.dirname(self.temp_db_path))
                print("🧹 Cleaned up test database")
            except Exception as e:
                print(f"⚠️  Could not clean up test database: {e}")
    
    def run_test_category(self, category: str, test_files: List[str]) -> bool:
        """Run a category of tests."""
        print(f"\n📋 Running {category} tests...")
        
        all_passed = True
        for test_file in test_files:
            if not os.path.exists(f"tests/{test_file}"):
                print(f"⚠️  Test file tests/{test_file} not found, skipping...")
                continue
                
            print(f"  🧪 Running {test_file}...")
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    f"tests/{test_file}", 
                    "-v", "--tb=short", "--no-header"
                ], capture_output=True, text=True, timeout=60)
                
                success = result.returncode == 0
                self.test_results[test_file] = success
                self.test_outputs[test_file] = result.stdout + result.stderr
                
                if success:
                    print(f"    ✅ {test_file} passed")
                else:
                    print(f"    ❌ {test_file} failed")
                    print(f"    📝 Error output:")
                    for line in result.stderr.split('\n'):
                        if line.strip():
                            print(f"       {line}")
                    all_passed = False
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏰ {test_file} timed out")
                self.test_results[test_file] = False
                self.test_outputs[test_file] = "Test timed out after 60 seconds"
                all_passed = False
            except Exception as e:
                print(f"    💥 {test_file} error: {e}")
                self.test_results[test_file] = False
                self.test_outputs[test_file] = str(e)
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Run all test categories."""
        print("🚀 Starting comprehensive test suite...")
        
        # Test categories in order of importance
        test_categories = {
            "Health & Connectivity": [
                "test_health.py",
                "test_database.py"
            ],
            "Authentication": [
                "test_password_hashing.py",
                "test_auth.py"
            ],
            "API Endpoints": [
                "test_api_endpoints.py"
            ]
        }
        
        all_passed = True
        
        for category, test_files in test_categories.items():
            category_passed = self.run_test_category(category, test_files)
            if not category_passed:
                all_passed = False
        
        return all_passed
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for passed in self.test_results.values() if passed)
        failed_tests = total_tests - passed_tests
        
        report = f"""
{'='*60}
📊 TEST EXECUTION REPORT
{'='*60}

📈 Summary:
   Total Tests: {total_tests}
   ✅ Passed: {passed_tests}
   ❌ Failed: {failed_tests}
   📊 Success Rate: {(passed_tests/total_tests*100):.1f if total_tests > 0 else 100.0}%

{'='*60}
📋 Detailed Results:
"""
        
        for test_file, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report += f"\n   {status} {test_file}"
            
            if not passed:
                report += f"\n      💥 Error Details:"
                for line in self.test_outputs[test_file].split('\n')[:5]:
                    if line.strip():
                        report += f"\n         {line}"
                if len(self.test_outputs[test_file].split('\n')) > 5:
                    report += f"\n         ... (truncated)"
        
        report += f"\n\n{'='*60}"
        
        if passed_tests == total_tests:
            report += "\n🎉 ALL TESTS PASSED! Ready for deployment."
        else:
            report += f"\n⚠️  {failed_tests} TESTS FAILED! Fix issues before deployment."
        
        report += f"\n{'='*60}\n"
        
        return report


async def main():
    """Main test execution function."""
    runner = TestRunner()
    
    try:
        # Setup
        runner.setup_test_environment()
        
        # Install dependencies
        print("📦 Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pytest", "pytest-asyncio", "pytest-httpx"
        ], check=True, capture_output=True)
        
        # Run tests
        all_passed = runner.run_all_tests()
        
        # Generate report
        report = runner.generate_report()
        print(report)
        
        # Save report to file
        with open("test_report.txt", "w") as f:
            f.write(report)
        print("📄 Test report saved to test_report.txt")
        
        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)
    finally:
        runner.cleanup_test_environment()


if __name__ == "__main__":
    asyncio.run(main())