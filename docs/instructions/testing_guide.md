# Testing Guide for Text-to-Speech Application

This document provides detailed guidance on testing the Text-to-Speech application, including both server-side and client-side testing strategies.

## Testing Layers

The application testing is organized into several layers:

1. **Unit Testing**: Testing individual functions and classes in isolation.
2. **Integration Testing**: Testing how components work together.
3. **Docker Environment Testing**: Testing the application within a Docker container.
4. **Client-Side Testing**: Testing JavaScript functionality.
5. **End-to-End Testing**: Testing the complete user flow.

## Required Test Cases

### Core Generator Functionality (Python)

- **API Key Handling**: Test retrieval of API key from arguments or environment variables.
- **Text Input Handling**: Test reading text from file and fallback to default text.
- **Text Chunking**: Test splitting text into manageable chunks.
  - Test with text shorter than the chunk limit
  - Test with text longer than the chunk limit
  - Test with text that has natural break points (periods, paragraphs)
- **Speech Generation**: Test the generation of speech for both short and long text.
  - Test with mock mode to avoid actual API calls
  - Test error handling (API errors, file writing errors)
- **Audio Stitching**: Test combining multiple audio segments into a single file.
  - Test with single chunk (no stitching needed)
  - Test with multiple chunks (stitching required)
- **Cost Calculation**: Test that cost is calculated correctly based on text length and model.

### Web Interface (Python/Flask)

- **Route Testing**: Test that all routes respond with the expected status codes.
- **Form Handling**: Test form submission and validation.
- **API Endpoints**: Test JSON API endpoints for speech generation and cost calculation.
- **History**: Test recording and retrieving generation history.
- **File Handling**: Test saving and serving audio files.

### Client-Side Functionality (JavaScript)

- **DOM Manipulation**: Test updating the DOM based on user interactions.
- **Event Handling**: Test event listeners and callbacks.
- **Form Validation**: Test client-side form validation.
- **API Interaction**: Test fetch requests to the application's API endpoints.
- **UI Updates**: Test updating UI elements based on API responses.

### Docker Environment

- **Container Startup**: Test that the Docker container starts correctly.
- **Service Availability**: Test that the service is accessible on the expected port.
- **Environment Variables**: Test that environment variables are properly set and used.
- **Volume Mounting**: Test that volumes are correctly mounted and files are persisted.

## Testing Tools

### Python Testing

- **pytest**: Main testing framework for Python code.
- **unittest.mock**: For mocking dependencies during tests.
- **requests**: For testing HTTP endpoints.

### JavaScript Testing

- **Jest**: Main testing framework for JavaScript code.
- **jsdom**: For simulating the DOM environment.
- **Puppeteer**: For browser automation and end-to-end testing.

### Docker Testing

- **requests**: For making HTTP requests to the containerized application.
- **docker-compose**: For managing the Docker container during tests.

## Key Test Scenarios

### Text-to-Speech Conversion Test Cases

1. **Short Text Conversion**:
   - Input: Text shorter than 3000 characters
   - Expected: Single API call, no chunking, direct audio generation

2. **Long Text Conversion**:
   - Input: Text longer than 3000 characters
   - Expected: Multiple API calls, text chunking, audio stitching

3. **Special Characters**:
   - Input: Text with special characters, non-Latin scripts, etc.
   - Expected: Correct handling and conversion

4. **Cost Calculation**:
   - Input: Various text lengths and models
   - Expected: Accurate cost calculation

### Error Handling Test Cases

1. **API Key Missing**:
   - Scenario: No API key provided
   - Expected: Appropriate error message

2. **API Error**:
   - Scenario: API returns an error
   - Expected: Graceful error handling, user notification

3. **Invalid Input**:
   - Scenario: Empty or invalid text
   - Expected: Validation error, user notification

4. **File System Error**:
   - Scenario: Unable to write to the output directory
   - Expected: Graceful error handling, user notification

## Testing Best Practices

1. **Isolation**: Each test should run in isolation without depending on other tests.
2. **Mocking**: Use mocks to avoid external dependencies (API calls, file I/O).
3. **Coverage**: Aim for high test coverage, especially for critical paths.
4. **Test Data**: Use representative test data that covers edge cases.
5. **Performance**: Keep tests fast to enable frequent execution during development.

## Continuous Integration

The application should be tested automatically on each code change. This can be accomplished with CI/CD pipelines that:

1. Run Python tests
2. Run JavaScript tests
3. Build and test the Docker container
4. Generate coverage reports

## Implementation Examples

### Python Test Example (pytest)

```python
def test_split_text_into_chunks():
    """Test splitting text into chunks."""
    # Test case 1: Text shorter than the limit
    short_text = "This is a short text."
    chunks = split_text_into_chunks(short_text, max_chars=100)
    assert len(chunks) == 1
    assert chunks[0] == short_text
    
    # Test case 2: Text longer than the limit
    long_text = "This is a longer text that should be split into multiple chunks."
    chunks = split_text_into_chunks(long_text, max_chars=20)
    assert len(chunks) > 1
    assert "".join(chunks) == long_text.replace(". ", ".")  # Account for period handling
```

### JavaScript Test Example (Jest)

```javascript
test('should calculate character count correctly', () => {
  // Setup
  document.getElementById.mockImplementation((id) => {
    if (id === 'text-input') return { value: 'Test text', length: 9 };
    if (id === 'char-count') return { textContent: '0' };
    return null;
  });
  
  // Call the function
  updateCharacterCount();
  
  // Assertions
  const charCount = document.getElementById('char-count');
  expect(charCount.textContent).toBe('9');
});
```

### Docker Test Example

```python
def test_health_endpoint():
    """Test that the health endpoint is responding in the Docker container."""
    response = requests.get("http://localhost:5001/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
``` 