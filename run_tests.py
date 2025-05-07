#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path

def run_django_backend_tests(project_root):
    """Run Django backend tests"""
    print("\n=== Running Django Backend Tests ===")
    try:
        # Run all tests within the backend.tests package
        print("\nRunning all backend tests...")
        result_all = subprocess.run(
            ['python', 'manage.py', 'test', 'backend.tests'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        print(result_all.stdout, flush=True) # Added flush=True here
        print(result_all.stderr, flush=True)  # Added flush=True here
        return result_all.returncode == 0
    except Exception as e:
        print(f"Error running Django tests: {e}")
        return False

def run_react_frontend_tests(frontend_dir):
    """Run React frontend tests using Vitest"""
    print("\n=== Running React Frontend Tests ===")
    try:
        # Run all tests within the tests directory
        print("\nRunning all frontend tests...")
        result_all = subprocess.run(
            ['npm', 'test', '--run'],  # Use --run to execute tests directly
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        print(result_all.stdout)
        print(result_all.stderr)
        return result_all.returncode == 0
    except Exception as e:
        print(f"Error running React tests: {e}")
        return False

def run_cypress_frontend_tests(frontend_dir):
    """Run Cypress E2E tests"""
    print("\n=== Running Cypress E2E Tests ===")
    try:
        # Run all tests within the tests/endtoend directory
        print("\nRunning all end-to-end tests...")
        result_all = subprocess.run(
            ['npm', 'run', 'cypress:run'], # Run all tests
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        print(result_all.stdout)
        print(result_all.stderr)
        return result_all.returncode == 0
    except Exception as e:
        print(f"Error running Cypress tests: {e}")
        return False

def main():
    # Get project root directory (where manage.py is located)
    project_root = Path('library_manager')
    frontend_dir = project_root / 'frontend'

    if not project_root.exists():
        print(f"Error: Project root directory not found at {project_root}")
        return False

    # Store test results
    results = {
        'backend': False
        # 'frontend': False,
        # 'e2e': False
    }

    # Run all tests
    # print("Starting all tests...\n")

    # Backend tests
    results['backend'] = run_django_backend_tests(project_root)

    # # Frontend tests
    # if frontend_dir.exists():
    #     results['frontend'] = run_react_frontend_tests(frontend_dir)
    #     results['e2e'] = run_cypress_frontend_tests(frontend_dir)  # Corrected line
    # else:
    #     print(f"Frontend directory not found at {frontend_dir}")

    # Print summary
    print("\n=== Test Summary ===")
    print(f"Backend Tests: {'PASSED' if results['backend'] else 'FAILED'}")
    # print(f"Frontend Tests: {'PASSED' if results['frontend'] else 'FAILED'}")
    # print(f"E2E Tests: {'PASSED' if results['e2e'] else 'FAILED'}")

    # Return overall success/failure
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)