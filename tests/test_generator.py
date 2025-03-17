import sys
import os
import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add the parent directory to sys.path to import the generator module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generator import get_api_key, get_input_text, generate_speech, main


# Tests for get_api_key function
def test_get_api_key_from_args():
    """Test that get_api_key retrieves API key from command-line arguments."""
    args = argparse.Namespace(api_key="test-api-key")
    with patch.dict(os.environ, {}, clear=True):  # Ensure no env variables
        result = get_api_key(args)
        assert result == "test-api-key", f"Expected 'test-api-key', got '{result}'"


def test_get_api_key_from_env():
    """Test that get_api_key retrieves API key from environment variable."""
    args = argparse.Namespace(api_key=None)
    with patch.dict(os.environ, {"OPENAI_API_KEY": "env-api-key"}, clear=True):
        result = get_api_key(args)
        assert result == "env-api-key", f"Expected 'env-api-key', got '{result}'"


def test_get_api_key_missing():
    """Test that get_api_key exits when API key is missing."""
    args = argparse.Namespace(api_key=None)
    with patch.dict(os.environ, {}, clear=True), \
         pytest.raises(SystemExit) as excinfo, \
         patch('builtins.print') as mock_print:
        get_api_key(args)
    assert excinfo.value.code == 1  # Should exit with code 1
    assert mock_print.call_count >= 1  # Should print error message


# Tests for get_input_text function
def test_get_input_text_success():
    """Test that get_input_text reads text correctly."""
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "Test text"
        result = get_input_text(Path('mock_file.txt'))
        assert result == "Test text", f"Expected 'Test text', got '{result}'"


def test_get_input_text_file_not_found():
    """Test that get_input_text handles missing files correctly."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = get_input_text(Path('nonexistent_file.txt'), "Default")
        assert result == "Default", f"Expected 'Default', got '{result}'"


def test_get_input_text_empty_file():
    """Test that get_input_text handles empty files correctly."""
    with patch('builtins.open', create=True) as mock_open, \
         patch('builtins.print') as mock_print:
        mock_open.return_value.__enter__.return_value.read.return_value = ""
        result = get_input_text(Path('empty_file.txt'), "Default for Empty")
        assert result == "Default for Empty", f"Expected 'Default for Empty', got '{result}'"
        mock_print.assert_called_once()  # Should print warning


def test_get_input_text_whitespace_only():
    """Test that get_input_text handles files with only whitespace correctly."""
    with patch('builtins.open', create=True) as mock_open, \
         patch('builtins.print') as mock_print:
        mock_open.return_value.__enter__.return_value.read.return_value = "   \n   \t   "
        result = get_input_text(Path('whitespace_file.txt'), "Default for Whitespace")
        assert result == "Default for Whitespace", f"Expected 'Default for Whitespace', got '{result}'"
        mock_print.assert_called_once()  # Should print warning


# Tests for generate_speech function
def test_generate_speech():
    """Test that generate_speech functions correctly."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.audio.speech.with_streaming_response.create.return_value.__enter__.return_value = mock_response
    
    result = generate_speech(
        mock_client, 
        "Test input", 
        Path("test_output.mp3"),
        "test-model",
        "test-voice"
    )
    
    assert result is True, f"Expected True, got {result}"
    mock_client.audio.speech.with_streaming_response.create.assert_called_once()
    mock_response.stream_to_file.assert_called_once()


def test_generate_speech_parameter_validation():
    """Test that generate_speech validates parameters correctly."""
    mock_client = MagicMock()
    
    # Test with None client
    with pytest.raises(AssertionError) as excinfo:
        generate_speech(None, "Test input", Path("test_output.mp3"))
    assert "client must be initialized" in str(excinfo.value)
    
    # Test with empty input text
    with pytest.raises(AssertionError) as excinfo:
        generate_speech(mock_client, "", Path("test_output.mp3"))
    assert "Input text cannot be empty" in str(excinfo.value)
    
    # Test with None speech_file_path
    with pytest.raises(AssertionError) as excinfo:
        generate_speech(mock_client, "Test input", None)
    assert "Speech file path must be specified" in str(excinfo.value)
    
    # Test with empty model
    with pytest.raises(AssertionError) as excinfo:
        generate_speech(mock_client, "Test input", Path("test_output.mp3"), "", "test-voice")
    assert "Model name must be specified" in str(excinfo.value)
    
    # Test with empty voice
    with pytest.raises(AssertionError) as excinfo:
        generate_speech(mock_client, "Test input", Path("test_output.mp3"), "test-model", "")
    assert "Voice name must be specified" in str(excinfo.value)


def test_generate_speech_with_different_models_and_voices():
    """Test that generate_speech works with different models and voices."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.audio.speech.with_streaming_response.create.return_value.__enter__.return_value = mock_response
    
    # Test with tts-1-hd model
    result = generate_speech(
        mock_client, 
        "Test input HD", 
        Path("test_output_hd.mp3"),
        "tts-1-hd",
        "alloy"
    )
    assert result is True
    
    # Check that the correct parameters were passed
    mock_client.audio.speech.with_streaming_response.create.assert_called_with(
        model="tts-1-hd",
        voice="alloy",
        input="Test input HD"
    )
    
    # Reset mock for next test
    mock_client.reset_mock()
    
    # Test with nova voice
    result = generate_speech(
        mock_client, 
        "Test input Nova", 
        Path("test_output_nova.mp3"),
        "tts-1",
        "nova"
    )
    assert result is True
    
    # Check that the correct parameters were passed
    mock_client.audio.speech.with_streaming_response.create.assert_called_with(
        model="tts-1",
        voice="nova",
        input="Test input Nova"
    )


# Tests for main function
def test_main_function():
    """Test that main function returns correct values in test mode."""
    with patch('pathlib.Path', MagicMock()), \
         patch('builtins.open', create=True) as mock_open:
        
        mock_open.return_value.__enter__.return_value.read.return_value = "Main test text"
        args = argparse.Namespace(
            api_key=None,
            input_file='test_input.txt',
            output_file='test_output.mp3',
            model='test-model',
            voice='test-voice',
            test=True
        )
        
        input_text, speech_file, model, voice = main(args)
        assert input_text == "Main test text", f"Expected 'Main test text', got '{input_text}'"
        assert str(speech_file) == "test_output.mp3", f"Expected 'test_output.mp3', got '{speech_file}'"
        assert model == "test-model", f"Expected 'test-model', got '{model}'"
        assert voice == "test-voice", f"Expected 'test-voice', got '{voice}'"


def test_main_function_with_args():
    """Test the main function with different argument combinations."""
    with patch('generator.get_api_key', return_value="test-key"), \
         patch('generator.OpenAI') as mock_openai, \
         patch('generator.get_input_text', return_value="Mocked text"), \
         patch('generator.generate_speech', return_value=True), \
         patch('generator.display_processing_info', return_value=True):

        # Test with custom input and output files
        args = argparse.Namespace(
            api_key="arg-key",
            input_file='custom_input.txt',
            output_file='custom_output.mp3',
            model='tts-1',
            voice='alloy',
            test=False,
            force=False  # Add the force parameter
        )

        result = main(args)
        assert result is True, "Main function should return True on success"
        
        # Test with force=True parameter
        args = argparse.Namespace(
            api_key="arg-key",
            input_file='custom_input.txt',
            output_file='custom_output.mp3',
            model='tts-1',
            voice='alloy',
            test=False,
            force=True  # Skip confirmation prompt
        )
        
        result = main(args)
        assert result is True, "Main function should return True on success"


def test_main_function_integration():
    """Test the entire pipeline in an integrated manner with mocks."""
    with patch('generator.get_api_key', return_value="test-key"), \
         patch('generator.OpenAI') as mock_openai, \
         patch('builtins.open', create=True) as mock_open, \
         patch('generator.Path', return_value=MagicMock()), \
         patch('generator.generate_speech', return_value=True), \
         patch('generator.display_processing_info', return_value=True):

        # Setup mock for file reading
        mock_open.return_value.__enter__.return_value.read.return_value = "Integration test text"

        # Run main with default arguments
        args = argparse.Namespace(
            api_key=None,
            input_file='default_input.txt',
            output_file='default_output.mp3',
            model='tts-1',
            voice='alloy',
            test=False,
            force=False  # Add the force parameter
        )

        result = main(args)
        assert result is True, "Main function should return True on success"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 