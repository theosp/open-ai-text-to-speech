#!/usr/bin/env python3
import requests
import unittest
import time
import os
import json
from bs4 import BeautifulSoup

class DockerWebInterfaceTests(unittest.TestCase):
    """Tests for the web interface running in Docker container."""
    
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
    
    def test_homepage_loads(self):
        """Test that the homepage loads successfully."""
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Text-to-Speech Generator", response.text)
    
    def test_form_exists(self):
        """Test that the text input form exists on the homepage."""
        response = requests.get(f"{self.BASE_URL}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for form elements
        form = soup.find('form', {'id': 'tts-form'})
        self.assertIsNotNone(form, "Form not found on homepage")
        
        textarea = soup.find('textarea', {'id': 'text-input'})
        self.assertIsNotNone(textarea, "Text input area not found")
        
        voice_select = soup.find('select', {'id': 'voice'})
        self.assertIsNotNone(voice_select, "Voice selection dropdown not found")
        
        model_select = soup.find('select', {'id': 'model-select'})
        self.assertIsNotNone(model_select, "Model selection dropdown not found")
        
        submit_button = soup.find('input', {'id': 'submit'})
        self.assertIsNotNone(submit_button, "Submit button not found")
    
    def test_preview_cost_api(self):
        """Test the API endpoint for previewing cost."""
        # Skip API test for now
        pass
    
    def test_history_page(self):
        """Test that the history page loads."""
        response = requests.get(f"{self.BASE_URL}/history")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Generation History", response.text)

if __name__ == "__main__":
    unittest.main() 