#!/usr/bin/env python3
"""
Test runner for Clara PM
Executes all test scripts in the tests directory
"""

import os
import sys
import importlib.util
import unittest
import time
import subprocess
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init()

def find_test_files():
    """Find all test files in the current directory"""
    test_files = []
    for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
        if file.startswith("test_") and file.endswith(".py") and file != "run_tests.py":
            test_files.append(file[:-3])  # Remove .py extension
    return test_files

def run_unittest_tests():
    """Run all unittest-based tests"""
    print(f"{Fore.CYAN}=== Running unittest tests ==={Style.RESET_ALL}")
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_standalone_tests():
    """Run standalone test scripts that don't use unittest"""
    print(f"{Fore.CYAN}=== Running standalone tests ==={Style.RESET_ALL}")
    test_files = find_test_files()
    success = True
    
    for test_module in test_files:
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{test_module}.py")
        
        # Check if the file contains unittest.TestCase
        with open(test_path, 'r') as f:
            content = f.read()
            is_unittest = 'unittest.TestCase' in content or 'TestCase' in content
        
        if not is_unittest:
            print(f"\n{Fore.YELLOW}Running {test_module}.py as standalone test{Style.RESET_ALL}")
            try:
                result = subprocess.run([sys.executable, test_path], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"{Fore.GREEN}✓ {test_module} - Success{Style.RESET_ALL}")
                    print(result.stdout)
                else:
                    success = False
                    print(f"{Fore.RED}✗ {test_module} - Failed{Style.RESET_ALL}")
                    print(result.stdout)
                    print(f"{Fore.RED}Error output:{Style.RESET_ALL}")
                    print(result.stderr)
            except Exception as e:
                success = False
                print(f"{Fore.RED}✗ {test_module} - Error: {str(e)}{Style.RESET_ALL}")
    
    return success

def main():
    """Run all tests"""
    print(f"{Fore.GREEN}=== Clara PM Test Suite ==={Style.RESET_ALL}")
    start_time = time.time()
    
    # Run unittest tests
    unittest_success = run_unittest_tests()
    
    # Run standalone tests
    standalone_success = run_standalone_tests()
    
    # Print summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{Fore.CYAN}=== Test Summary ==={Style.RESET_ALL}")
    print(f"Total time: {duration:.2f} seconds")
    
    if unittest_success and standalone_success:
        print(f"{Fore.GREEN}All tests passed successfully!{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}Some tests failed. Please check the output above.{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 