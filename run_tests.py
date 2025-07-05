#!/usr/bin/env python3
"""
Simple test runner to avoid PyO3 import issues.
"""

import subprocess
import sys
import os

def run_tests():
    """Run tests using subprocess to avoid PyO3 issues."""
    print("Running tests to avoid PyO3 import issues...")
    
    # Run basic functionality test first
    print("\n1. Running basic functionality test...")
    result1 = subprocess.run([sys.executable, "test_basic_functionality.py"], 
                           capture_output=True, text=True)
    
    if result1.returncode == 0:
        print("✅ Basic functionality test passed")
        print(result1.stdout)
    else:
        print("❌ Basic functionality test failed")
        print(result1.stderr)
    
    # Run improved modules tests
    print("\n2. Running improved modules tests...")
    result2 = subprocess.run([sys.executable, "-m", "pytest", 
                            "tests/test_improved_modules.py", "-v"], 
                           capture_output=True, text=True)
    
    if result2.returncode == 0:
        print("✅ Improved modules tests passed")
        print(result2.stdout)
    else:
        print("❌ Improved modules tests failed")
        print(result2.stderr)
    
    # Run multi-issue tests
    print("\n3. Running multi-issue tests...")
    result3 = subprocess.run([sys.executable, "-m", "pytest", 
                            "tests/test_multi_issue_upload_with_subtasks.py", "-v"], 
                           capture_output=True, text=True)
    
    if result3.returncode == 0:
        print("✅ Multi-issue tests passed")
        print(result3.stdout)
    else:
        print("❌ Multi-issue tests failed")
        print(result3.stderr)
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Basic functionality: {'✅ PASS' if result1.returncode == 0 else '❌ FAIL'}")
    print(f"Improved modules: {'✅ PASS' if result2.returncode == 0 else '❌ FAIL'}")
    print(f"Multi-issue: {'✅ PASS' if result3.returncode == 0 else '❌ FAIL'}")
    
    total_failures = sum(1 for r in [result1, result2, result3] if r.returncode != 0)
    if total_failures == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_failures} test suite(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests()) 