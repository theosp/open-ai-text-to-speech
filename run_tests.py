#!/usr/bin/env python3
"""
Test runner script for the text-to-speech generator.
Run this script to execute all tests and generate coverage reports.
"""

import argparse
import sys
import subprocess


def run_tests(args):
    """Run the tests with the specified options."""
    cmd = ["python", "-m", "pytest"]
    
    # Add coverage reporting if requested
    if args.coverage:
        cmd.extend(["--cov=generator"])
        if args.html:
            cmd.extend(["--cov-report=html"])
    
    # Add specific test files if provided
    if args.test_files:
        cmd.extend(args.test_files)
    
    # Add verbose mode if requested
    if args.verbose:
        cmd.append("-v")
    
    # Add failing test details if requested
    if args.detailed_errors:
        cmd.append("-vv")
    
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run the text-to-speech tests.')
    parser.add_argument('--coverage', '-c', action='store_true',
                        help='Generate coverage report')
    parser.add_argument('--html', action='store_true',
                        help='Generate HTML coverage report')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show verbose output')
    parser.add_argument('--detailed-errors', '-d', action='store_true',
                        help='Show detailed errors for failing tests')
    parser.add_argument('test_files', nargs='*',
                        help='Specific test files to run (defaults to all tests)')
    
    args = parser.parse_args()
    
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main()) 