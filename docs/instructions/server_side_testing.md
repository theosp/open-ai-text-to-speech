# Server-Side Testing Guide

This document provides detailed guidance on writing and running server-side tests for the Text-to-Speech application.

## Server-Side Test Structure

The server-side tests are primarily located in the `tests` directory and use pytest as the testing framework.

### Key Files and Directories

- `tests/test_app.py`: Tests for Flask application functionality
- `tests/test_generator.py`: Tests for the text-to-speech generator functionality
- `tests/test_utils.py`: Tests for utility functions
- `tests/__init__.py`: Init file for the tests package
- `tests/conftest.py`: Pytest fixtures shared across test files

## Running the Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov=generator --cov=utils

# Run specific test file
pytest tests/test_app.py

# Run tests with verbose output
pytest -v

# Run tests and output coverage report
pytest --cov=app --cov=generator --cov=utils --cov-report=term-missing
```

## Coverage Reports

For detailed coverage reports, run:

```bash
pytest --cov=app --cov=generator --cov=utils --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory, which you can view in a browser.

## Writing Tests

### Flask Application Tests

Tests for the Flask application should:

1. Use Flask test client for sending requests
2. Mock external API calls (OpenAI)
3. Check response status codes and content
4. Verify template rendering

Example:

```python
def test_index_route(client):
    """Test that the index route returns a successful response."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Text to Speech' in response.data
```

### Generator Tests

Tests for the TTS generator should:

1. Mock the OpenAI API responses
2. Test text chunking and stitching functionality
3. Verify error handling and edge cases
4. Check correct handling of different voices and models

Example:

```python
def test_chunk_text():
    """Test text chunking functionality."""
    text = "This is a test. " * 1000  # Long text
    chunks = chunk_text(text, 3000)
    
    # Check that all chunks are below the maximum size
    assert all(len(chunk) <= 3000 for chunk in chunks)
    
    # Check that all content is preserved
    assert ''.join(chunks) == text
```

### Utility Function Tests

Tests for utility functions should:

1. Verify correct calculations (e.g., cost)
2. Test input validation
3. Check error handling

Example:

```python
def test_calculate_cost():
    """Test cost calculation for different models and text lengths."""
    # Standard model
    assert calculate_cost(100, "standard") == 0.00015
    
    # HD model
    assert calculate_cost(100, "hd") == 0.0003
    
    # Test longer text
    assert calculate_cost(1000, "standard") == 0.0015
```

## Required Test Cases

### 1. API Routes and Endpoints

- Test GET request to index route returns 200 status and correct template
- Test POST request to generate endpoint with valid data
- Test handling of missing API key
- Test health check endpoint

### 2. Text Processing

- Test text chunking for texts of varying lengths
- Test handling of special characters and formatting
- Test edge cases (empty text, extremely long text)

### 3. TTS Generation

- Test successful TTS generation with mocked OpenAI responses
- Test handling of OpenAI API errors
- Test voice selection functionality
- Test different models (standard vs. HD)

### 4. Cost Calculation

- Test cost preview calculation for both models
- Test cost calculation for varying text lengths
- Test cost calculation for multi-chunk texts

### 5. Audio Processing

- Test audio file generation
- Test audio stitching for multiple chunks
- Test temporary file handling and cleanup

### 6. Error Handling

- Test invalid input handling
- Test missing API key scenarios
- Test OpenAI API failure scenarios
- Test rate limit handling

## Test Fixtures

Create reusable fixtures in `conftest.py`:

```python
import pytest
from app import create_app
from unittest.mock import patch

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_openai():
    """Mock for OpenAI API calls."""
    with patch('openai.audio.speech.create') as mock_speech:
        # Configure the mock to return a sample audio content
        mock_speech.return_value.content = b'mock audio content'
        yield mock_speech
```

## Mocking OpenAI API

For OpenAI API calls, use mocking to avoid actual API usage during tests:

```python
def test_generate_speech(mock_openai):
    """Test speech generation with mocked OpenAI API."""
    generator = TextToSpeechGenerator(api_key="test_key")
    audio_content = generator.generate_speech("Test text", "alloy", "standard")
    
    # Verify the API was called with correct parameters
    mock_openai.assert_called_once_with(
        model="tts-1",
        voice="alloy",
        input="Test text"
    )
    
    # Verify we got the expected mock content back
    assert audio_content == b'mock audio content'
```

## Testing Text Chunking and Audio Stitching

### Case 1: Short Text (No Stitching)

```python
def test_short_text_no_stitching(mock_openai):
    """Test generation of short text that doesn't require stitching."""
    generator = TextToSpeechGenerator(api_key="test_key")
    text = "This is a short test text."
    
    result = generator.generate(text, "alloy", "standard")
    
    # Verify OpenAI API was called once
    assert mock_openai.call_count == 1
    
    # Verify no stitching was performed
    # (Implementation depends on how stitching is tracked in your code)
```

### Case 2: Long Text (Requires Stitching)

```python
def test_long_text_with_stitching(mock_openai, tmpdir):
    """Test generation of long text that requires chunking and stitching."""
    generator = TextToSpeechGenerator(api_key="test_key")
    # Create text that exceeds the chunk size
    text = "This is a test. " * 1000
    
    # Configure mock to return different content for different chunks
    mock_openai.side_effect = [
        type('obj', (object,), {'content': b'chunk1'}),
        type('obj', (object,), {'content': b'chunk2'}),
        type('obj', (object,), {'content': b'chunk3'})
    ]
    
    result = generator.generate(text, "alloy", "standard")
    
    # Verify OpenAI API was called multiple times
    assert mock_openai.call_count > 1
    
    # Additional assertions would depend on how stitching is implemented
    # and how the result is returned
```

## Best Practices

1. **Isolation**: Keep tests independent of each other
2. **Mocking**: Mock external APIs to avoid real API calls
3. **Coverage**: Aim for high test coverage, especially for core functionality
4. **Fixtures**: Use fixtures for common setup and teardown
5. **Parameterization**: Use pytest's parameterize feature for testing multiple scenarios
6. **Clean Up**: Ensure temporary files are cleaned up after tests
7. **CI Integration**: Make sure tests can run in CI environment
8. **Fast Execution**: Keep tests fast to enable frequent execution 