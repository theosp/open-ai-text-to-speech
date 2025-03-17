import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from app import app, client, generate_voice_samples, SUPPORTED_VOICES

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_generate_voice_samples_route_disabled(client):
    """Test that voice sample generation is disabled by default"""
    # Ensure environment variable is not set
    with patch.dict(os.environ, {'ALLOW_SAMPLE_GENERATION': 'false'}):
        response = client.get('/generate-voice-samples')
        assert response.status_code == 302  # Redirect expected
        # Should redirect to index
        assert b'Redirecting...' in response.data

def test_generate_voice_samples_route_enabled(client):
    """Test that voice sample generation works when enabled"""
    # Mock the OpenAI client response
    mock_response = MagicMock()
    mock_response.content = b'mock audio content'
    
    # Mock the OpenAI client
    with patch.dict(os.environ, {'ALLOW_SAMPLE_GENERATION': 'true'}):
        with patch('app.client.audio.speech.create', return_value=mock_response):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Patch the static folder to use our temp directory
                with patch('app.app.static_folder', temp_dir):
                    # Create samples directory
                    samples_dir = os.path.join(temp_dir, 'audio', 'samples')
                    os.makedirs(samples_dir, exist_ok=True)
                    
                    # Call the route
                    response = client.get('/generate-voice-samples')
                    
                    # Check response
                    assert response.status_code == 200
                    
                    # Check that samples were generated
                    for voice in SUPPORTED_VOICES:
                        sample_path = os.path.join(samples_dir, f"{voice}.mp3")
                        # If the file was created, it should exist
                        assert os.path.exists(sample_path)
                        
                        # Check file content
                        with open(sample_path, 'rb') as f:
                            content = f.read()
                            assert content == b'mock audio content'

def test_generate_voice_samples_handles_errors(client):
    """Test that voice sample generation handles errors gracefully"""
    # Mock the OpenAI client to raise an exception
    def mock_create_error(*args, **kwargs):
        raise Exception("API error")
    
    # Mock the OpenAI client
    with patch.dict(os.environ, {'ALLOW_SAMPLE_GENERATION': 'true'}):
        with patch('app.client.audio.speech.create', side_effect=mock_create_error):
            with tempfile.TemporaryDirectory() as temp_dir:
                # Patch the static folder to use our temp directory
                with patch('app.app.static_folder', temp_dir):
                    # Create samples directory
                    samples_dir = os.path.join(temp_dir, 'audio', 'samples')
                    os.makedirs(samples_dir, exist_ok=True)
                    
                    # Call the route
                    response = client.get('/generate-voice-samples')
                    
                    # Should still return 200 with error messages
                    assert response.status_code == 200
                    
                    # Response should include error information
                    assert b'error:' in response.data 