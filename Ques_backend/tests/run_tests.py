#!/usr/bin/env python3
"""
Ques Backend Test Runner
Comprehensive testing suite for database verification and integration testing
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.append(str(Path(__file__).parent.parent))

class TestRunner:
    def __init__(self):
        self.backend_root = Path(__file__).parent.parent
        self.test_root = Path(__file__).parent
        self.passed_tests = []
        self.failed_tests = []
        
    def print_banner(self, message):
        """Print a formatted banner message"""
        print("\n" + "="*60)
        print(f" {message}")
        print("="*60)
        
    def run_test(self, test_path, description):
        """Run a single test and track results"""
        print(f"\n🧪 Running: {description}")
        print(f"   File: {test_path}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=self.backend_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            end_time = time.time()
            
            if result.returncode == 0:
                print(f"   ✅ PASSED ({end_time - start_time:.2f}s)")
                self.passed_tests.append((description, test_path))
                return True
            else:
                print(f"   ❌ FAILED ({end_time - start_time:.2f}s)")
                print(f"   Error: {result.stderr[:200]}...")
                self.failed_tests.append((description, test_path, result.stderr))
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT (60s)")
            self.failed_tests.append((description, test_path, "Test timed out"))
            return False
        except Exception as e:
            print(f"   💥 ERROR: {str(e)}")
            self.failed_tests.append((description, test_path, str(e)))
            return False
    
    def run_database_tests(self):
        """Run all database verification tests"""
        self.print_banner("DATABASE VERIFICATION TESTS")
        
        db_tests = [
            ("check_db_state.py", "Database State Verification"),
            ("check_new_tables.py", "New Tables Validation"),
            ("check_user_swipes.py", "User Swipes Table Verification"),
            ("verify_chat_tables.py", "Chat System Tables Verification"),
        ]
        
        db_test_dir = self.test_root / "database"
        
        for test_file, description in db_tests:
            test_path = db_test_dir / test_file
            if test_path.exists():
                self.run_test(test_path, description)
            else:
                print(f"   ⚠️  SKIPPED: {description} (file not found)")
    
    def run_integration_tests(self):
        """Run all integration tests"""
        self.print_banner("INTEGRATION TESTS")
        
        integration_tests = [
            ("test_api_endpoints.py", "API Endpoints Testing"),
            ("test_chat_integration.py", "Chat System Integration"),
            ("test_final_integration.py", "Complete System Integration"),
            ("test_tpns_integration.py", "TPNS Integration Testing"),
        ]
        
        integration_test_dir = self.test_root / "integration"
        
        for test_file, description in integration_tests:
            test_path = integration_test_dir / test_file
            if test_path.exists():
                self.run_test(test_path, description)
            else:
                print(f"   ⚠️  SKIPPED: {description} (file not found)")
    
    def run_unit_tests(self):
        """Run unit tests if they exist"""
        self.print_banner("UNIT TESTS")
        
        unit_test_dir = self.test_root / "unit"
        if unit_test_dir.exists():
            for test_file in unit_test_dir.glob("test_*.py"):
                description = f"Unit Test: {test_file.stem}"
                self.run_test(test_file, description)
        else:
            print("   ℹ️  No unit tests directory found")
    
    def print_summary(self):
        """Print test execution summary"""
        self.print_banner("TEST EXECUTION SUMMARY")
        
        total_tests = len(self.passed_tests) + len(self.failed_tests)
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {len(self.passed_tests)}")
        print(f"❌ Failed: {len(self.failed_tests)}")
        
        if self.passed_tests:
            print("\n🎉 PASSED TESTS:")
            for description, test_path in self.passed_tests:
                print(f"   ✅ {description}")
        
        if self.failed_tests:
            print("\n💥 FAILED TESTS:")
            for description, test_path, error in self.failed_tests:
                print(f"   ❌ {description}")
                print(f"      File: {test_path}")
                print(f"      Error: {error[:100]}...")
        
        success_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        return len(self.failed_tests) == 0
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_banner("QUES BACKEND TEST SUITE")
        print("Starting comprehensive test execution...")
        
        # Run database tests first
        self.run_database_tests()
        
        # Run integration tests
        self.run_integration_tests()
        
        # Run unit tests if they exist
        self.run_unit_tests()
        
        # Print summary
        all_passed = self.print_summary()
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
            return 0
        else:
            print("\n⚠️  SOME TESTS FAILED! Please review and fix issues.")
            return 1

def main():
    """Main entry point"""
    runner = TestRunner()
    
    # Check if specific test type requested
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "database":
            runner.run_database_tests()
        elif test_type == "integration":
            runner.run_integration_tests()
        elif test_type == "unit":
            runner.run_unit_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: database, integration, unit")
            return 1
        
        return runner.print_summary()
    else:
        # Run all tests
        return runner.run_all_tests()

if __name__ == "__main__":
    exit(main())