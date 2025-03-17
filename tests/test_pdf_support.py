import os
import sys
import io
import pytest
from unittest.mock import MagicMock, patch, mock_open
import uuid

# Add the parent directory to sys.path to import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import extract_text_from_pdf, app

class TestPDFSupport:
    """Tests for PDF extraction functionality."""
    
    def test_extract_text_from_pdf_success(self):
        """Test successful text extraction from a PDF file."""
        # Mock PyPDF2.PdfReader behavior
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"
        
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            # Setup mock PDF reader with a single page
            mock_pdf_reader.return_value.pages = [mock_page]
            
            # Create a mock PDF file-like object
            mock_pdf_file = io.BytesIO(b"mock PDF content")
            
            # Call the function with the mock file
            result = extract_text_from_pdf(mock_pdf_file)
            
            # Verify the results
            assert result == "Test PDF content"
            assert mock_pdf_reader.called
            assert mock_page.extract_text.called
    
    def test_extract_text_from_pdf_multiple_pages(self):
        """Test extracting text from a multi-page PDF file."""
        # Mock pages with different content
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            # Setup mock PDF reader with multiple pages
            mock_pdf_reader.return_value.pages = [mock_page1, mock_page2]
            
            # Create a mock PDF file-like object
            mock_pdf_file = io.BytesIO(b"mock PDF content")
            
            # Call the function with the mock file
            result = extract_text_from_pdf(mock_pdf_file)
            
            # Verify the results
            assert "Page 1 content" in result
            assert "Page 2 content" in result
            assert mock_page1.extract_text.called
            assert mock_page2.extract_text.called
    
    def test_extract_text_from_pdf_empty_page(self):
        """Test handling of empty pages in a PDF file."""
        # Mock pages with different content
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = ""  # Empty page
        
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Page 3 content"
        
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            # Setup mock PDF reader with multiple pages
            mock_pdf_reader.return_value.pages = [mock_page1, mock_page2, mock_page3]
            
            # Create a mock PDF file-like object
            mock_pdf_file = io.BytesIO(b"mock PDF content")
            
            # Call the function with the mock file
            result = extract_text_from_pdf(mock_pdf_file)
            
            # Verify the results
            assert "Page 1 content" in result
            assert "Page 3 content" in result
            # Empty page should not add a new line
            assert "Page 1 content\n\nPage 3 content" == result.strip()
    
    def test_extract_text_from_pdf_exception(self):
        """Test handling of exceptions during PDF text extraction."""
        with patch('PyPDF2.PdfReader') as mock_pdf_reader:
            # Setup mock PDF reader to raise an exception
            mock_pdf_reader.side_effect = Exception("PDF error")
            
            # Create a mock PDF file-like object
            mock_pdf_file = io.BytesIO(b"mock PDF content")
            
            # The function should raise an exception
            with pytest.raises(Exception) as excinfo:
                extract_text_from_pdf(mock_pdf_file)
            
            # Verify the exception message
            assert "Failed to extract text from PDF" in str(excinfo.value)
    
    def test_extract_text_from_pdf_logging(self):
        """Test that errors are properly logged."""
        with patch('PyPDF2.PdfReader') as mock_pdf_reader, \
             patch('app.app.logger.error') as mock_logger:
            # Setup mock PDF reader to raise an exception
            mock_pdf_reader.side_effect = Exception("PDF error")
            
            # Create a mock PDF file-like object
            mock_pdf_file = io.BytesIO(b"mock PDF content")
            
            # The function should raise an exception
            with pytest.raises(Exception):
                extract_text_from_pdf(mock_pdf_file)
            
            # Verify the logger was called
            mock_logger.assert_called_once()
            assert "Error extracting text from PDF" in mock_logger.call_args[0][0]


class TestPDFSupportIntegration:
    """Integration tests for the PDF support functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        with app.test_client() as client:
            yield client
    
    def test_index_accepts_pdf_upload(self, client):
        """Test that the index page accepts PDF file uploads."""
        with patch('app.extract_text_from_pdf') as mock_extract:
            # Setup the mock to return test content
            mock_extract.return_value = "Extracted PDF content"
            
            # Create a mock PDF file
            mock_pdf = (io.BytesIO(b"mock PDF data"), "test.pdf")
            
            # Make a POST request with the mock PDF file
            response = client.post(
                '/',
                data={
                    'pdf_file': mock_pdf,
                    'voice': 'alloy',
                    'model': 'tts-1'
                },
                content_type='multipart/form-data'
            )
            
            # Check if the mock was called
            assert mock_extract.called
            
            # Check if we get redirected to the result page
            assert response.status_code in (302, 303)  # Redirect status code
            assert 'result' in response.location
    
    def test_api_accepts_pdf_upload(self, client):
        """Test that the API endpoint accepts PDF file uploads."""
        with patch('app.extract_text_from_pdf') as mock_extract, \
             patch('app.generate_speech') as mock_generate, \
             patch('uuid.uuid4') as mock_uuid, \
             patch('os.path.getsize') as mock_getsize:
            # Setup the mocks
            mock_extract.return_value = "Extracted API PDF content"
            mock_generate.return_value = None  # No return value needed
            mock_uuid.return_value = "test-123"
            mock_getsize.return_value = 12345  # Mock file size
            
            # Create a mock PDF file
            mock_pdf = (io.BytesIO(b"mock PDF data"), "api-test.pdf")
            
            # Make a POST request with the mock PDF file
            response = client.post(
                '/api/generate',
                data={
                    'pdf_file': mock_pdf,
                    'voice': 'alloy',
                    'model': 'tts-1'
                },
                content_type='multipart/form-data'
            )
            
            # Check if the response is successful
            assert response.status_code == 200
            assert mock_extract.called
            
            # Check response JSON
            json_data = response.get_json()
            assert json_data['success'] is True
            assert json_data['filename'] == 'test-123.mp3'
            assert json_data['source_type'] == 'PDF'
            assert json_data['original_filename'] == 'api-test.pdf' 