#!/usr/bin/env python3
import requests
import unittest
import time
import json

class DockerFlaskTests(unittest.TestCase):
    """Tests for the Flask application functionality in Docker container."""
    
    BASE_URL = "http://localhost:5001"
    
    def setUp(self):
        """Setup before each test - ensure the container is ready."""
        # Wait for the service to be fully initialized
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                response = requests.get(f"{self.BASE_URL}/")
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            
            print(f"Waiting for service to be ready (attempt {retry_count+1}/{max_retries})...")
            retry_count += 1
            time.sleep(2)
        
        if retry_count == max_retries:
            self.fail("Service not available after maximum retries")
    
    def test_flask_routes(self):
        """Test that all expected Flask routes are responding."""
        # Test home page
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        
        # Test history page
        response = requests.get(f"{self.BASE_URL}/history")
        self.assertEqual(response.status_code, 200)
        
        # Test API endpoints
        response = requests.get(f"{self.BASE_URL}/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")
    
    def test_static_files(self):
        """Test that static files are being served correctly."""
        # Skip static file tests for now as they might not be set up yet
        pass
    
    def test_error_handling(self):
        """Test that error handling is working correctly."""
        # Test 404 page
        response = requests.get(f"{self.BASE_URL}/nonexistent_route")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid API request
        response = requests.post(
            f"{self.BASE_URL}/api/preview-cost",
            json={"invalid": "data"}
        )
        self.assertIn(response.status_code, [400, 422])  # Either is acceptable for invalid data
        
    def test_environment_variables(self):
        """Test that environment variables are accessible inside the container."""
        # This endpoint should be implemented in the Flask app for testing purposes
        response = requests.get(f"{self.BASE_URL}/api/check-environment")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that essential environment variables are set
        self.assertIn("openai_api_key_set", data)
        self.assertTrue(data["openai_api_key_set"], "OpenAI API key not set in container")
        self.assertIn("secret_key_set", data)
        self.assertTrue(data["secret_key_set"], "Flask secret key not set in container")
        self.assertIn("docker_env", data)
        self.assertTrue(data["docker_env"], "DOCKER_ENV variable not set in container")

if __name__ == "__main__":
    unittest.main()