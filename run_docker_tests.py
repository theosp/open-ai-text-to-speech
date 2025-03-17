#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import time
import requests

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import requests
        import bs4
    except ImportError:
        print("Installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])

def check_docker_running():
    """Check if Docker is running and the container is up."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=text-to-speech", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def ensure_container_running():
    """Ensure the text-to-speech container is running."""
    if not check_docker_running():
        print("Text-to-speech container is not running. Starting it...")
        try:
            # Check if the container exists but is stopped
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=text-to-speech", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            
            if result.stdout.strip():
                # Container exists, start it
                subprocess.run(["docker", "start", result.stdout.strip()], check=True)
            else:
                # Container doesn't exist, start with docker-compose
                subprocess.run(["docker", "compose", "up", "-d"], check=True)
                
            # Wait for container to be ready
            print("Waiting for container to be ready...")
            time.sleep(5)
            
            # Verify container is running
            if not check_docker_running():
                print("Failed to start container.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Error starting container: {e}")
            return False
    
    # Check if the web service is responding
    try:
        response = requests.get("http://localhost:5001/")
        if response.status_code == 200:
            print("Container is running and web service is responding.")
            return True
        else:
            print(f"Web service returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error connecting to web service: {e}")
        return False

def run_tests(args):
    """Run the test suite."""
    test_command = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    
    if args.test_file:
        test_command = [sys.executable, args.test_file]
    
    try:
        subprocess.run(test_command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Run tests against the Dockerized text-to-speech application.")
    parser.add_argument("--test-file", help="Run a specific test file instead of discovering all tests")
    parser.add_argument("--skip-dependency-check", action="store_true", help="Skip dependency check")
    args = parser.parse_args()
    
    if not args.skip_dependency_check:
        check_dependencies()
    
    if not ensure_container_running():
        print("Cannot proceed with tests because the container is not running properly.")
        sys.exit(1)
    
    print("\nRunning tests against the Dockerized application...")
    success = run_tests(args)
    
    if success:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 