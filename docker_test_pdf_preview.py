import os
import sys
import io
import pytest
from unittest.mock import MagicMock, patch, mock_open
import json

# Add the parent directory to sys.path to import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import app, extract_text_from_pdf

class TestPDFPreview:
    """Tests for PDF preview functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        with app.test_client() as client:
            yield client
    
    def test_preview_with_pdf_only(self, client):
        """Test cost preview with PDF input only."""
        with patch('app.extract_text_from_pdf') as mock_extract:
            # Mock the PDF text extraction
            mock_extract.return_value = "PDF extracted text for testing"
            
            # Create a mock PDF file
            mock_pdf = (io.BytesIO(b"mock PDF content"), "test.pdf")
            
            # Make a POST request with the mock PDF file
            response = client.post(
                '/preview',
                data={
                    'model': 'tts-1',
                    'pdf_file': mock_pdf
                },
                content_type='multipart/form-data'
            )
            
            # Verify the response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'text_length' in data
            assert 'num_chunks' in data
            assert 'cost' in data
            assert data['text_length'] == len("PDF extracted text for testing")
            assert data['num_chunks'] == 1
            expected_cost = len("PDF extracted text for testing") * 0.000015
            assert data['cost'] == expected_cost
            
            # Verify the mock was called
            mock_extract.assert_called_once()

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 