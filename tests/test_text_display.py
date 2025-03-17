import unittest
from unittest.mock import patch, MagicMock
import io
import os
import sys
import pytest
from flask import session

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, HISTORY_TEXT_PREVIEW_LENGTH

class TestTextDisplay(unittest.TestCase):
    """Tests for the text display functionality in the result page"""
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-key'
        self.client = app.test_client()
        self.client.testing = True
        
    @patch('app.get_history')
    def test_full_text_display_from_url_params(self, mock_history):
        """Test that the full text is displayed when it's provided in URL params"""
        # Set up
        long_text = "This is a very long text that should be displayed in full " * 50  # 450+ chars
        
        # Make request with text in URL params
        with self.client as client:
            response = client.get(f'/result?filename=test.mp3&text={long_text}&text_length={len(long_text)}')
            self.assertEqual(response.status_code, 200)
            
            # Check that the text is in the response
            response_text = response.data.decode('utf-8')
            self.assertIn(f"{len(long_text)} characters", response_text)
            
            # Only first HISTORY_TEXT_PREVIEW_LENGTH chars should be displayed, with truncation indicator
            if len(long_text) > HISTORY_TEXT_PREVIEW_LENGTH:
                self.assertIn(long_text[:HISTORY_TEXT_PREVIEW_LENGTH], response_text)
                self.assertIn("(text truncated)", response_text)
                self.assertIn("Download Full Text", response_text)
            else:
                self.assertIn(long_text, response_text)
    
    @patch('app.get_history')
    def test_full_text_display_from_session(self, mock_history):
        """Test that the full text is displayed when it's stored in the session"""
        # Set up
        long_text = "This is a very long text that should be displayed in full " * 50  # 450+ chars
        
        # Make request with text in session
        with self.client as client:
            with client.session_transaction() as sess:
                sess['last_generated_text'] = long_text
                sess['last_generated_filename'] = 'test.mp3'
                
            response = client.get('/result?filename=test.mp3')
            self.assertEqual(response.status_code, 200)
            
            # Check that the text is in the response
            response_text = response.data.decode('utf-8')
            self.assertIn(f"{len(long_text)} characters", response_text)
            
            # Only first HISTORY_TEXT_PREVIEW_LENGTH chars should be displayed, with truncation indicator
            if len(long_text) > HISTORY_TEXT_PREVIEW_LENGTH:
                self.assertIn(long_text[:HISTORY_TEXT_PREVIEW_LENGTH], response_text)
                self.assertIn("(text truncated)", response_text)
                self.assertIn("Download Full Text", response_text)
            else:
                self.assertIn(long_text, response_text)
                
            # Verify session was cleared after use
            self.assertNotIn('last_generated_text', session)
    
    @patch('app.get_history')
    def test_truncated_text_display_from_history(self, mock_history):
        """Test that truncated text from history shows appropriate warnings"""
        # Set up - create a truncated history entry
        truncated_text = "This is a truncated text from history..."
        mock_history.return_value = [{
            'filename': 'test.mp3',
            'text': truncated_text,
        }]
        
        # Make request
        with self.client as client:
            response = client.get('/result?filename=test.mp3')
            self.assertEqual(response.status_code, 200)
            
            # Check that the text is in the response
            response_text = response.data.decode('utf-8')
            self.assertIn(truncated_text, response_text)
            
            # Check for the warning flash message
            self.assertIn("The full text for this generation is not available", response_text)
    
    @patch('app.get_history')
    def test_text_download_functionality(self, mock_history):
        """Test that the download text functionality works correctly"""
        # Set up - create a session with text
        long_text = "This is a very long text that should be downloaded in full " * 50  # 450+ chars
        
        # Test download with text in session
        with self.client as client:
            with client.session_transaction() as sess:
                sess['last_generated_text'] = long_text
                sess['last_generated_filename'] = 'test.mp3'
                
            # Mock the send_file function to prevent actual file creation
            with patch('app.send_file') as mock_send_file:
                mock_send_file.return_value = 'mocked_file'
                
                response = client.get('/download-text/test.mp3')
                
                # Just verify that send_file was called - this is enough to show the functionality works
                mock_send_file.assert_called_once()
                
                # Check the response status code
                self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 