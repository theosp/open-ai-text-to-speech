import os
import sys
import io
import pytest
from unittest.mock import MagicMock, patch, mock_open
import json

# Add the parent directory to sys.path to import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    
    def test_preview_with_text_only(self, client):
        """Test cost preview with text input only."""
        response = client.post(
            '/preview',
            data={
                'text': 'Sample text for testing cost preview',
                'model': 'tts-1'
            }
        )
        
        # Verify the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'text_length' in data
        assert 'num_chunks' in data
        assert 'cost' in data
        assert data['text_length'] == 36  # Length of the sample text
        assert data['num_chunks'] == 1
        assert data['cost'] == 36 * 0.000015  # Cost for tts-1 model
    
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
    
    def test_preview_with_text_and_pdf(self, client):
        """Test cost preview with both text and PDF input."""
        with patch('app.extract_text_from_pdf') as mock_extract:
            # Mock the PDF text extraction
            mock_extract.return_value = "PDF extracted text for testing"
            
            # Create a mock PDF file
            mock_pdf = (io.BytesIO(b"mock PDF content"), "test.pdf")
            
            # Make a POST request with both text and PDF
            response = client.post(
                '/preview',
                data={
                    'text': 'Sample text input',
                    'model': 'tts-1',
                    'pdf_file': mock_pdf
                },
                content_type='multipart/form-data'
            )
            
            # Verify the response
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Combined text should be: "Sample text input\n\nPDF extracted text for testing"
            combined_text = "Sample text input\n\nPDF extracted text for testing"
            assert data['text_length'] == len(combined_text)
            assert data['num_chunks'] == 1
            expected_cost = len(combined_text) * 0.000015
            assert data['cost'] == expected_cost
            
            # Verify the mock was called
            mock_extract.assert_called_once()
    
    def test_preview_with_pdf_extraction_error(self, client):
        """Test handling of PDF extraction errors in preview."""
        with patch('app.extract_text_from_pdf') as mock_extract:
            # Mock the PDF extraction to raise an exception
            mock_extract.side_effect = Exception("PDF extraction error")
            
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
            assert 'error' in data
            assert 'PDF extraction error' in data['error']
            
            # Verify the mock was called
            mock_extract.assert_called_once()
    
    def test_preview_with_no_text_and_no_pdf(self, client):
        """Test handling of empty request in preview."""
        response = client.post(
            '/preview',
            data={
                'model': 'tts-1'
            }
        )
        
        # Verify the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No text provided' in data['error']
    
    def test_preview_with_high_def_model(self, client):
        """Test cost calculation with high-definition model."""
        response = client.post(
            '/preview',
            data={
                'text': 'Sample text for testing cost preview',
                'model': 'tts-1-hd'
            }
        )
        
        # Verify the response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['text_length'] == 36  # Length of the sample text
        assert data['cost'] == 36 * 0.000030  # Cost for tts-1-hd model
    
    def test_preview_with_long_text_from_pdf(self, client):
        """Test cost preview with long text from PDF that spans multiple chunks."""
        with patch('app.extract_text_from_pdf') as mock_extract:
            # Create a text with more than 4000 characters
            long_text = "A" * 5000
            mock_extract.return_value = long_text
            
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
            assert data['text_length'] == 5000
            assert data['num_chunks'] == 2  # Should be split into 2 chunks
            expected_cost = 5000 * 0.000015
            assert data['cost'] == expected_cost 