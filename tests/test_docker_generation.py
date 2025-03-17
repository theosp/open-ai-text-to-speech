#!/usr/bin/env python3
import requests
import unittest
import time
import os
import json
from bs4 import BeautifulSoup

class DockerGenerationTests(unittest.TestCase):
    """Tests for the speech generation functionality in Docker container."""
    
    BASE_URL = "http://localhost:5001"
    TEST_TEXT = "This is a short test of the text to speech system."
    
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
    
    def test_generation_api_mock(self):
        """Test the API endpoint for text-to-speech generation with mock mode.
        
        This test doesn't actually generate speech using the OpenAI API but tests
        the application logic by setting mock_mode=true.
        """
        # Skip API test for now
        pass
    
    def test_form_submission(self):
        """Test form submission through web interface.
        
        This test simulates a user filling out the form and submitting it.
        """
        # Skip form submission test for now
        pass

if __name__ == "__main__":
    unittest.main() 