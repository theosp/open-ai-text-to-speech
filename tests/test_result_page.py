import pytest
from app import app
import json
import os
import humanize
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Create a test client for the app."""
    with app.test_client() as client:
        with app.app_context():
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            app.config['OPENAI_API_KEY'] = 'test_key'
            # Enable sessions in testing
            app.config['SECRET_KEY'] = 'test_secret_key'
        yield client

def mock_history_json():
    """Return a mock history json for testing."""
    return [
        {
            "id": "test1",
            "filename": "test1.mp3",
            "timestamp": "2023-01-01 12:00:00",
            "text": "Test text 1",
            "voice": "alloy",
            "model": "tts-1",
            "text_length": 10,
            "num_chunks": 1,
            "processing_time": "0.5 seconds",
            "filesize": "10KB"
        }
    ]

@pytest.fixture
def mock_openai():
    """Mock the OpenAI API calls."""
    with patch('generator.OpenAI') as mock_openai:
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        
        # Mock audio.speech.create
        mock_response = MagicMock()
        mock_response.read.return_value = b'mock_audio_data'
        mock_instance.audio.speech.create.return_value = mock_response
        
        yield mock_instance

@pytest.fixture
def mock_history(monkeypatch):
    """Mock the history file operations."""
    # Mock get_history function
    monkeypatch.setattr('app.get_history', lambda: mock_history_json())
    
    # Mock os.path.exists
    monkeypatch.setattr('os.path.exists', lambda path: True)
    
    # Mock os.path.getsize
    monkeypatch.setattr('os.path.getsize', lambda path: 10 * 1024)  # 10KB
    
    # Mock humanize.naturalsize
    monkeypatch.setattr('humanize.naturalsize', lambda size: '10.0 KB')

class TestResultPage:
    
    def test_text_displayed_in_result_page(self, client, mock_openai, mock_history):
        """Test that text is correctly displayed on the result page."""
        # Submit form with sample text
        with patch('app.generate_speech', return_value='test_output.mp3'):
            response = client.post('/', data={
                'text': 'Sample text for testing',
                'voice': 'alloy',
                'model': 'tts-1'
            }, follow_redirects=True)
        
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that the correct template was rendered
        html = response.data.decode('utf-8')
        assert 'Audio Generated Successfully' in html
        
        # Check that the input text is displayed
        assert 'Sample text for testing' in html

    def test_large_text_handling(self, client, mock_openai, mock_history):
        """Test that large text is properly handled via session."""
        large_text = "A" * 2000  # Text too large for URL params
        
        # Submit form with large text
        with patch('app.generate_speech', return_value='test_output.mp3'):
            response = client.post('/', data={
                'text': large_text,
                'voice': 'alloy',
                'model': 'tts-1'
            }, follow_redirects=True)
                
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that at least part of the large text appears in response
        html = response.data.decode('utf-8')
        assert large_text[:50] in html
    
    def test_text_retrieval_from_history(self, client, mock_history):
        """Test retrieval of text from history when not in URL or session."""
        # Access result page with only filename
        response = client.get('/result?filename=test_file.mp3')
        
        # Check that text was retrieved from history
        assert b'Sample text for testing' in response.data
    
    def test_empty_text_handling(self, client):
        """Test that empty text is properly handled."""
        # Submit form with empty text
        response = client.post('/', data={
            'text': '',
            'voice': 'alloy',
            'model': 'tts-1'
        })
        
        # Should not redirect but show an error
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'Please enter some text' in html or 'Text cannot be empty' in html

    def test_delete_all_audio(self, client, monkeypatch):
        """Test the delete all audio functionality."""
        # Mock clear_all_history to return True
        monkeypatch.setattr('app.clear_all_history', lambda: True)
        
        # Call the delete-all route
        response = client.get('/delete-all', follow_redirects=True)
        
        # Check for success message
        assert b'All audio files deleted successfully' in response.data
        
        # Check that we were redirected to history page
        assert b'Generation History' in response.data 