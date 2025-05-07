#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path
import platform # For OS-specific logic
import re # Import the regular expression module

def strip_ansi_codes(text):
    """Removes ANSI escape codes from a string."""
    if text is None:
        return ""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

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
            text=True,
            check=False # Explicitly set check=False
        )
        print(result_all.stdout, flush=True)
        print(result_all.stderr, flush=True)
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
        use_shell = platform.system() == "Windows"
        # Using npx to ensure vitest is found and executed correctly
        command = ['npx', 'vitest', 'run']

        # Prepare environment for the subprocess
        env = os.environ.copy()
        env["NO_COLOR"] = "1" # Disable ANSI color output from Vitest

        result_all = subprocess.run(
            command,
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            shell=use_shell, # Use shell=True on Windows for npm
            check=False, # Explicitly set check=False
            encoding='utf-8',  # Specify UTF-8 encoding
            errors='replace',   # Handle potential encoding errors gracefully
            env=env # Pass the modified environment
        )
        
        # Strip ANSI codes from stdout and stderr before printing
        stdout_cleaned = strip_ansi_codes(result_all.stdout)
        stderr_cleaned = strip_ansi_codes(result_all.stderr)

        print(stdout_cleaned)
        if stderr_cleaned: # Only print if there's actual stderr content
            print("Errors from React tests:", file=sys.stderr)
            print(stderr_cleaned, file=sys.stderr)
        return result_all.returncode == 0
    except FileNotFoundError:
        # This would catch if 'npx' itself is not found, which is unlikely if npm is installed.
        print(f"Error running React tests: 'npx' command not found. Ensure Node.js and npm are installed and in your PATH.")
        return False
    except Exception as e:
        print(f"Error running React tests: {e}")
        return False

def run_cypress_frontend_tests(frontend_dir):
    """Run Cypress E2E tests"""
    print("\n=== Running Cypress E2E Tests ===")
    try:
        # Run all tests within the tests/endtoend directory
        print("\nRunning all end-to-end tests...")
        use_shell = platform.system() == "Windows"
        command = ['npm', 'run', 'cypress:run']

        result_all = subprocess.run(
            command,
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            shell=use_shell, # Use shell=True on Windows for npm
            check=False # Explicitly set check=False
        )
        print(result_all.stdout)
        if result_all.stderr:
            print("Errors from Cypress tests:", file=sys.stderr)
            print(result_all.stderr, file=sys.stderr)
        return result_all.returncode == 0
    except FileNotFoundError:
        print(f"Error running Cypress tests: 'npm' command not found. Ensure Node.js and npm are installed and in your PATH.")
        return False
    except Exception as e:
        print(f"Error running Cypress tests: {e}")
        return False

def main():
    # Robust path definition relative to this script file
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir / 'library_manager'
    frontend_dir = project_root / 'frontend'

    if not project_root.exists():
        print(f"Error: Project root directory not found at {project_root}")
        # Corrected to return False, not just print.
        # However, the script intends to sys.exit(1) later if not all pass,
        # so direct return might be bypassed by sys.exit logic.
        # For consistency, let's ensure it affects the overall success status.
        return False 

    results = {
        'backend': False,
        'frontend': False,
        'e2e': False
    }

    # Run all tests
    # print("Starting all tests...\n") # Original line, can be kept if desired

    # results['backend'] = run_django_backend_tests(project_root)

    # Frontend tests
    if frontend_dir.exists():
        results['frontend'] = run_react_frontend_tests(frontend_dir)
        # results['e2e'] = run_cypress_frontend_tests(frontend_dir)
    else:
        print(f"Frontend directory not found at {frontend_dir}")
        # 'frontend' and 'e2e' results will remain False

    # Print summary
    print("\n=== Test Summary ===")
    # Use .get() for safety, though keys are pre-initialized
    print(f"Backend Tests: {'PASSED' if results.get('backend') else 'FAILED'}")
    print(f"Frontend Tests: {'PASSED' if results.get('frontend') else 'FAILED'}")
    # print(f"E2E Tests: {'PASSED' if results.get('e2e') else 'FAILED'}")

    # Return overall success/failure
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)