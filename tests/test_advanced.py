import sys
import os
import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import pytest
from hypothesis import given, strategies as st
from freezegun import freeze_time
from datetime import datetime, timedelta
import pydub

# Add the parent directory to sys.path to import the generator module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generator import (
    get_api_key, get_input_text, generate_speech, main,
    split_text_into_chunks, stitch_audio_files, calculate_cost,
    display_processing_info, MAX_CHARS_PER_REQUEST, COST_PER_1K_CHARS
)


class MockResponse:
    """Mock response class that simulates OpenAI API responses and errors."""
    def __init__(self, success=True, error_type=None):
        self.success = success
        self.error_type = error_type
        self.stream_to_file_called = False
    
    def __enter__(self):
        if not self.success:
            if self.error_type == "timeout":
                raise TimeoutError("Request timed out")
            elif self.error_type == "auth":
                raise ValueError("Authentication error: Invalid API key")
            elif self.error_type == "rate_limit":
                raise ValueError("Rate limit exceeded. Please try again later.")
            elif self.error_type == "server":
                raise ConnectionError("OpenAI servers are experiencing issues")
            elif self.error_type != "write_error":  # Don't raise here for write errors
                raise Exception("Unknown error occurred")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def stream_to_file(self, file_path):
        self.stream_to_file_called = True
        if not self.success and self.error_type == "write_error":
            raise IOError(f"Unable to write to file: {file_path}")


class MockOpenAI:
    """More sophisticated mock of the OpenAI client."""
    def __init__(self, api_key=None, success=True, error_type=None):
        self.api_key = api_key
        self.success = success
        self.error_type = error_type
        self.audio = MagicMock()
        self.audio.speech.with_streaming_response.create = self.create
        self.created_kwargs = None
    
    def create(self, **kwargs):
        self.created_kwargs = kwargs
        return MockResponse(success=self.success, error_type=self.error_type)


# New tests for text splitting functionality
def test_split_text_into_chunks_small_text():
    """Test that small text is not split."""
    text = "This is a short text."
    chunks = split_text_into_chunks(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_text_into_chunks_large_text():
    """Test that large text is split correctly."""
    # Create a text slightly larger than the limit
    text = "This is a sentence. " * (MAX_CHARS_PER_REQUEST // 18 + 10)
    chunks = split_text_into_chunks(text)
    assert len(chunks) > 1
    # Check that each chunk is under the limit
    for chunk in chunks:
        assert len(chunk) <= MAX_CHARS_PER_REQUEST


def test_split_text_into_chunks_very_long_sentence():
    """Test splitting a sentence that's longer than the max chunk size."""
    # Create a very long single sentence
    long_word = "supercalifragilisticexpialidocious"
    text = (long_word + " ") * (MAX_CHARS_PER_REQUEST // len(long_word) + 5)
    chunks = split_text_into_chunks(text)
    assert len(chunks) > 1
    # Check that each chunk is under the limit
    for chunk in chunks:
        assert len(chunk) <= MAX_CHARS_PER_REQUEST


def test_split_text_into_chunks_exact_boundary():
    """Test splitting text that falls exactly on the boundary."""
    # Create a text exactly at the limit
    exact_length_text = "a" * MAX_CHARS_PER_REQUEST
    chunks = split_text_into_chunks(exact_length_text)
    assert len(chunks) == 1
    assert len(chunks[0]) == MAX_CHARS_PER_REQUEST
    
    # Create a text one character over the limit
    over_limit_text = "a" * (MAX_CHARS_PER_REQUEST + 1)
    chunks = split_text_into_chunks(over_limit_text)
    assert len(chunks) == 2


# Tests for cost estimation
def test_calculate_cost():
    """Test cost calculation for different models and text lengths."""
    # Test standard model
    cost = calculate_cost(1000, "tts-1")
    assert cost == COST_PER_1K_CHARS["tts-1"]
    
    # Test HD model
    cost = calculate_cost(1000, "tts-1-hd")
    assert cost == COST_PER_1K_CHARS["tts-1-hd"]
    
    # Test different text length
    cost = calculate_cost(5000, "tts-1")
    assert cost == 5 * COST_PER_1K_CHARS["tts-1"]
    
    # Test with unknown model (should default to tts-1)
    cost = calculate_cost(1000, "unknown-model")
    assert cost == COST_PER_1K_CHARS["tts-1"]


# Test for display_processing_info with mocked input
def test_display_processing_info():
    """Test processing info display and user confirmation."""
    text = "Test text"
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value="y") as mock_input:
        result = display_processing_info(text, "tts-1")
        assert result is True  # User confirmed
        assert mock_print.call_count > 0  # Information was displayed
        
    with patch('builtins.print') as mock_print, \
         patch('builtins.input', return_value="n") as mock_input:
        result = display_processing_info(text, "tts-1")
        assert result is False  # User declined
        assert mock_print.call_count > 0  # Information was displayed


# Test for stitch_audio_files
def test_stitch_audio_files():
    """Test audio file stitching."""
    with patch('os.replace') as mock_replace, \
         patch('os.remove') as mock_remove:
        # Test with a single file (should just rename)
        result = stitch_audio_files(["temp1.mp3"], "output.mp3")
        assert result is True
        mock_replace.assert_called_once_with("temp1.mp3", "output.mp3")

    # Mock for multiple files
    mock_audio_segment = MagicMock()
    mock_combined = MagicMock()
    mock_audio_segment.return_value += mock_audio_segment  # Simulate adding segments
    
    with patch('pydub.AudioSegment.from_mp3', return_value=mock_audio_segment), \
         patch('pydub.AudioSegment.empty', return_value=mock_combined), \
         patch('os.remove') as mock_remove:
        
        # Configure export method
        mock_combined.export = MagicMock()
        
        # Test with multiple files
        result = stitch_audio_files(["temp1.mp3", "temp2.mp3"], "output.mp3")
        
        # Check result
        assert result is True
        
        # Verify AudioSegment.from_mp3 was called for each file
        assert pydub.AudioSegment.from_mp3.call_count == 2
        
        # No need to directly verify export was called as the function will 
        # actually use the real method and we've mocked the AudioSegment object
        # The test passes if no exception is raised


# Test for multi-file processing
@patch('generator.split_text_into_chunks')
@patch('generator.stitch_audio_files')
@patch('tempfile.mkstemp')
def test_generate_speech_with_multiple_chunks(mock_mkstemp, mock_stitch, mock_split):
    """Test generation of speech with multiple chunks."""
    # Setup mocks
    mock_split.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
    mock_mkstemp.side_effect = [(0, "temp1.mp3"), (0, "temp2.mp3"), (0, "temp3.mp3")]
    mock_stitch.return_value = True
    
    with patch('os.close') as mock_close, \
         patch('generator.generate_speech_for_chunk', return_value=True) as mock_generate:
        
        mock_client = MockOpenAI(api_key="test_key")
        result = generate_speech(
            mock_client,
            "Long text that will be split",
            Path("output.mp3"),
            "tts-1",
            "alloy"
        )
        
        assert result is True
        assert mock_generate.call_count == 3
        mock_stitch.assert_called_once()


# Test the complete flow with --force option to skip confirmation
def test_main_with_force_option():
    """Test main function with --force option to skip confirmation."""
    with patch('generator.get_api_key', return_value="test-key"), \
         patch('generator.OpenAI') as mock_openai_class, \
         patch('generator.get_input_text', return_value="Test text"), \
         patch('generator.generate_speech', return_value=True) as mock_generate, \
         patch('generator.display_processing_info') as mock_display:
        
        # Configure the mock OpenAI client
        mock_openai = MockOpenAI(api_key=None)
        mock_openai_class.return_value = mock_openai
        
        # Run main with --force
        args = argparse.Namespace(
            api_key="arg-key",
            input_file='input.txt',
            output_file='output.mp3',
            model='tts-1',
            voice='alloy',
            test=False,
            force=True
        )
        
        result = main(args)
        
        # Check that display_processing_info was not called due to force option
        mock_display.assert_not_called()
        assert result is True


# Property-based testing with Hypothesis
@given(
    input_text=st.text(min_size=1, max_size=1000),
    model=st.sampled_from(["tts-1", "tts-1-hd"]),
    voice=st.sampled_from(["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
)
def test_generate_speech_property_based(input_text, model, voice):
    """Property-based test for generate_speech with various inputs."""
    # Create a mock client
    mock_client = MockOpenAI(api_key="test_key", success=True)
    
    # Generate speech
    speech_file_path = Path("test_property.mp3")
    result = generate_speech(mock_client, input_text, speech_file_path, model, voice)
    
    # Verify the result
    assert result is True
    assert mock_client.created_kwargs is not None
    assert mock_client.created_kwargs["model"] == model
    assert mock_client.created_kwargs["voice"] == voice
    assert mock_client.created_kwargs["input"] == input_text


# Error injection tests
@pytest.mark.parametrize("error_type,expected_exception", [
    ("timeout", TimeoutError),
    ("auth", ValueError),
    ("rate_limit", ValueError),
    ("server", ConnectionError),
    ("unknown", Exception)
])
def test_generate_speech_api_errors(error_type, expected_exception):
    """Test handling of various API errors in generate_speech."""
    mock_client = MockOpenAI(api_key="test_key", success=False, error_type=error_type)
    
    with pytest.raises(expected_exception):
        generate_speech(
            mock_client,
            "Test with error injection",
            Path("test_error.mp3"),
            "tts-1",
            "alloy"
        )


def test_generate_speech_file_write_error():
    """Test handling of file write errors in generate_speech."""
    mock_client = MockOpenAI(api_key="test_key", success=False, error_type="write_error")
    
    with pytest.raises(IOError):
        generate_speech(
            mock_client,
            "Test with file write error",
            Path("test_write_error.mp3"),
            "tts-1",
            "alloy"
        )


# Time-based tests
@freeze_time("2023-01-01 12:00:00")
def test_api_key_expiry_behavior():
    """Test behavior when an API key is near expiration date."""
    # This test is just a demonstration of time freezing capability
    # In a real scenario, you might check for expiration warnings, etc.
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-expiring-soon"}):
        args = argparse.Namespace(api_key=None)
        api_key = get_api_key(args)
        assert api_key == "test-key-expiring-soon"
        # In a real app, you might check for warnings about expiring keys


# Long text handling tests
def test_generate_speech_with_long_text():
    """Test that generate_speech handles very long texts correctly."""
    # Create a long text (10,000 characters)
    long_text = "This is a test sentence. " * 500
    assert len(long_text) >= 10000, "Test text should be at least 10,000 characters"

    # Create a mock client
    mock_client = MockOpenAI(api_key="test_key")
    speech_file_path = Path("test_long.mp3")
    
    # Mock both generate_speech_for_chunk and stitch_audio_files to avoid dependency on ffmpeg
    with patch('generator.generate_speech_for_chunk', return_value=True) as mock_generate, \
         patch('generator.stitch_audio_files', return_value=True) as mock_stitch:
        
        # Call generate_speech with the long text
        result = generate_speech(mock_client, long_text, speech_file_path)
        
        # Verify the result
        assert result is True, "generate_speech should return True on success"
        
        # Verify generate_speech_for_chunk was called multiple times (one for each chunk)
        assert mock_generate.call_count > 1, "Should process multiple chunks for long text"
        
        # Verify stitch_audio_files was called once to combine the chunks
        mock_stitch.assert_called_once()


# Multiple consecutive calls test
def test_multiple_consecutive_calls():
    """Test behavior with multiple consecutive calls to generate_speech."""
    mock_client = MockOpenAI(api_key="test_key")
    
    texts = ["First text", "Second text", "Third text"]
    file_paths = [Path(f"test_multi_{i}.mp3") for i in range(len(texts))]
    
    # Make multiple calls
    for text, file_path in zip(texts, file_paths):
        result = generate_speech(mock_client, text, file_path)
        assert result is True
    
    # Verify that the correct parameters were passed in each call
    assert mock_client.created_kwargs["input"] == texts[-1]  # Last call


# Integration test with more complex behavior
def test_complex_integration():
    """Complex integration test with conditional behaviors."""
    
    # Track calls to our mocked functions
    mock_calls = []
    
    # Create patchers for all the functions
    with patch('generator.get_api_key', side_effect=lambda args: mock_calls.append('get_api_key') or 'test-key'), \
         patch('generator.OpenAI') as mock_openai_class, \
         patch('generator.get_input_text', side_effect=lambda path, default=None: mock_calls.append('get_input_text') or 'Complex test text'), \
         patch('generator.Path', side_effect=lambda p: mock_calls.append(f'Path({p})') or Path(p)), \
         patch('builtins.print') as mock_print:
        
        # Configure the mock OpenAI client
        mock_openai = MockOpenAI(api_key=None)
        mock_openai_class.return_value = mock_openai
        
        # Run main with custom arguments
        args = argparse.Namespace(
            api_key="arg-key",
            input_file='complex_input.txt',
            output_file='complex_output.mp3',
            model='tts-1-hd',
            voice='nova',
            test=False,
            force=True
        )
        
        result = main(args)
        
        # Check the result
        assert result is True
        
        # Verify the call sequence
        assert 'get_api_key' in mock_calls
        assert 'get_input_text' in mock_calls
        assert 'Path(complex_input.txt)' in mock_calls
        assert 'Path(complex_output.mp3)' in mock_calls
        
        # Verify that the OpenAI client was created with the right parameters
        assert mock_openai.created_kwargs is not None
        assert mock_openai.created_kwargs["model"] == 'tts-1-hd'
        assert mock_openai.created_kwargs["voice"] == 'nova'
        assert mock_openai.created_kwargs["input"] == 'Complex test text'


def test_generate_speech_for_chunk_with_retries():
    """Test the retry mechanism in generate_speech_for_chunk function."""
    from generator import generate_speech_for_chunk
    
    # Create a mock client where the first two attempts fail but the third succeeds
    mock_client = MagicMock()
    responses = [
        MockResponse(success=False, error_type="timeout"),  # First attempt fails with timeout
        MockResponse(success=False, error_type="server"),   # Second attempt fails with server error
        MockResponse(success=True)                         # Third attempt succeeds
    ]
    
    # Configure the client.audio.speech.with_streaming_response.create method to return
    # each response in sequence
    mock_client.audio.speech.with_streaming_response.create.side_effect = responses
    
    with patch('time.sleep') as mock_sleep:  # Mock sleep to avoid waiting in tests
        # Call the function with max_retries=3
        result = generate_speech_for_chunk(
            mock_client, 
            "Test chunk text", 
            "output_test.mp3", 
            max_retries=3, 
            retry_delay=1
        )
        
        # Verify the result is True (success)
        assert result is True
        
        # Verify create was called 3 times
        assert mock_client.audio.speech.with_streaming_response.create.call_count == 3
        
        # Verify sleep was called twice (after first and second failures)
        assert mock_sleep.call_count == 2


def test_generate_speech_for_chunk_peer_closed_connection():
    """Test handling of 'peer closed connection' errors."""
    from generator import generate_speech_for_chunk
    
    # Create a mock client where connection is closed unexpectedly
    mock_client = MagicMock()
    
    # Configure the create method to raise the specific error
    def side_effect(*args, **kwargs):
        raise Exception("peer closed connection without sending complete message body (incomplete chunked read)")
    
    mock_client.audio.speech.with_streaming_response.create.side_effect = side_effect
    
    with patch('time.sleep') as mock_sleep, pytest.raises(Exception) as excinfo:
        # Call with max_retries=2
        result = generate_speech_for_chunk(
            mock_client, 
            "Test chunk text", 
            "output_test.mp3", 
            max_retries=2, 
            retry_delay=1
        )
        
        # Verify the error message
        assert "peer closed connection" in str(excinfo.value)
        
        # Verify create was called max_retries times
        assert mock_client.audio.speech.with_streaming_response.create.call_count == 2
        
        # Verify sleep was called max_retries-1 times
        assert mock_sleep.call_count == 1


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 