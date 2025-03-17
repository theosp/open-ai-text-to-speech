# Advanced Test Scenarios Guide

This document outlines specific advanced test scenarios required for the Text-to-Speech application, with a focus on edge cases and complex functionality.

## Key Test Scenarios

### 1. Text Input and Character Counting

#### Current Coverage
The application already has tests for:
- Character counter initialization and updates
- Handling empty text input
- Validating text input on form submission

#### Suggested Improvements
- Add tests for very large text inputs (100K+ characters)
- Test with special characters, emojis, and different languages
- Test line breaks and whitespace handling

### 2. Cost Calculation

#### Current Coverage
The application has tests for:
- Basic cost calculation for standard model
- Cost calculation for HD model
- Cost calculation for different text lengths
- Handling of unknown models

#### Suggested Improvements
- Add property-based tests to verify cost calculation algorithm
- Test more edge cases (very small and very large inputs)
- Test boundary cases where text length crosses the 1K character threshold

### 3. Text-to-Speech Conversion

#### Current Coverage
The application has tests for:
- Basic TTS generation with both models
- Different voice options
- Error handling for API failures

#### Suggested Improvements
- Add more comprehensive mocking of OpenAI API responses
- Test the complete end-to-end flow with integration tests
- Add tests for handling API rate limits

### 4. Audio Stitching Cases

#### Case 1: Short Text (No Stitching Required)

**Test Scenario:**
Text under the maximum character limit (4096 characters) that doesn't require chunking or stitching.

**Test Implementation:**

```python
def test_short_text_no_stitching():
    """Test generation of speech with text short enough to not require chunking."""
    # Setup
    mock_client = MockOpenAI(api_key="test_key")
    short_text = "This is a short test text that doesn't need chunking."
    output_path = Path("output_short.mp3")
    
    # Mock the split_text_into_chunks function to verify it returns a single chunk
    with patch('generator.split_text_into_chunks', return_value=[short_text]) as mock_split, \
         patch('generator.generate_speech_for_chunk', return_value=True) as mock_generate:
        
        # Call the function
        result = generate_speech(
            mock_client,
            short_text,
            output_path,
            "tts-1",
            "alloy"
        )
        
        # Assertions
        assert result is True
        mock_split.assert_called_once_with(short_text)
        mock_generate.assert_called_once()
        # Verify that stitch_audio_files was called with just one file
        # (implementation depends on how the code is structured)
```

#### Case 2: Long Text (Stitching Required)

**Test Scenario:**
Text exceeding the maximum character limit that requires chunking and stitching.

**Test Implementation:**

```python
def test_long_text_with_stitching():
    """Test generation of speech with text that requires chunking and stitching."""
    # Setup
    mock_client = MockOpenAI(api_key="test_key")
    # Create text that will be split into multiple chunks
    long_text = "This is a test sentence. " * 250  # Roughly 5000 characters
    output_path = Path("output_long.mp3")
    
    # Create chunks that should be returned by split_text_into_chunks
    chunks = [
        "This is a test sentence. " * 83,
        "This is a test sentence. " * 83,
        "This is a test sentence. " * 84
    ]
    
    # Mock the relevant functions
    with patch('generator.split_text_into_chunks', return_value=chunks) as mock_split, \
         patch('tempfile.mkstemp', side_effect=[(0, "temp1.mp3"), (0, "temp2.mp3"), (0, "temp3.mp3")]), \
         patch('os.close') as mock_close, \
         patch('generator.generate_speech_for_chunk', return_value=True) as mock_generate, \
         patch('generator.stitch_audio_files', return_value=True) as mock_stitch:
        
        # Call the function
        result = generate_speech(
            mock_client,
            long_text,
            output_path,
            "tts-1",
            "alloy"
        )
        
        # Assertions
        assert result is True
        mock_split.assert_called_once_with(long_text)
        assert mock_generate.call_count == 3
        mock_stitch.assert_called_once_with(
            ["temp1.mp3", "temp2.mp3", "temp3.mp3"],
            str(output_path)
        )
```

**Edge Cases to Test:**

1. **Boundary Conditions:**
   - Test with text exactly at the maximum limit
   - Test with text just over the limit
   - Test with empty chunks

2. **Error Handling:**
   - Test when one chunk fails to generate
   - Test when audio stitching fails
   - Test with corrupted temporary files

3. **Performance:**
   - Test with very large texts (10+ chunks)
   - Measure memory usage during stitching
   - Measure processing time for large texts

### 5. User Interface Interaction

#### Current Coverage
The application has tests for:
- Setting up event listeners
- Updating the character counter
- Showing the cost preview
- Displaying the processing indicator

#### Suggested Improvements
- Add more comprehensive Puppeteer tests for browser interactions
- Test form submission with different input combinations
- Test the audio player functionality after generation

## Implementing New Tests

### Python Test for Chunking and Stitching

Add the following test to `tests/test_advanced.py`:

```python
def test_chunking_and_stitching_integration():
    """Integration test for the full chunking and stitching process."""
    # Create a mock client
    mock_client = MockOpenAI(api_key="test_key")
    
    # Create a text that will require multiple chunks
    long_text = "This is a test sentence. " * 250  # Roughly 5000 characters
    output_path = Path("output_integrated.mp3")
    
    # Setup mocks for audio segments
    mock_segment1 = MagicMock()
    mock_segment2 = MagicMock()
    mock_combined = MagicMock()
    
    with patch('generator.split_text_into_chunks', return_value=["Chunk 1", "Chunk 2"]) as mock_split, \
         patch('tempfile.mkstemp', side_effect=[(0, "temp1.mp3"), (0, "temp2.mp3")]), \
         patch('os.close') as mock_close, \
         patch('generator.generate_speech_for_chunk', return_value=True) as mock_generate, \
         patch('pydub.AudioSegment.from_mp3', side_effect=[mock_segment1, mock_segment2]), \
         patch('pydub.AudioSegment.empty', return_value=mock_combined), \
         patch('os.remove') as mock_remove:
        
        # Configure the mock segments
        mock_combined += mock_segment1
        mock_combined += mock_segment2
        mock_combined.export = MagicMock()
        
        # Call the function
        result = generate_speech(
            mock_client,
            long_text,
            output_path,
            "tts-1",
            "alloy"
        )
        
        # Verify results
        assert result is True
        mock_split.assert_called_once_with(long_text)
        assert mock_generate.call_count == 2
        assert pydub.AudioSegment.from_mp3.call_count == 2
        mock_combined.export.assert_called_once_with(str(output_path), format="mp3")
```

### JavaScript Test for UI Interaction

Add the following test to `client-tests/browser.test.js`:

```javascript
describe('Text-to-Speech UI Interaction', () => {
  test('Adding text to textarea updates character count', async () => {
    // Navigate to the page
    await page.goto('http://localhost:5001/');
    
    // Get the initial character count
    const initialCount = await page.$eval('#char-count', el => el.textContent);
    
    // Enter text in the textarea
    await page.type('#text-input', 'Hello, this is a test.');
    
    // Wait for the character count to update
    await page.waitForFunction(
      (initialCount) => document.querySelector('#char-count').textContent !== initialCount,
      {},
      initialCount
    );
    
    // Get the updated character count
    const updatedCount = await page.$eval('#char-count', el => el.textContent);
    
    // Verify the character count matches the text length
    expect(updatedCount).toBe('22');
  });
  
  test('Cost preview shows correct calculation', async () => {
    // Navigate to the page
    await page.goto('http://localhost:5001/');
    
    // Enter text in the textarea
    await page.type('#text-input', 'This is a test text with exactly fifty characters in it.');
    
    // Click the cost preview button
    await page.click('#preview-btn');
    
    // Wait for the cost preview to be displayed
    await page.waitForSelector('#cost-preview[style*="display: block"]');
    
    // Get the displayed values
    const previewLength = await page.$eval('#preview-length', el => el.textContent);
    const previewChunks = await page.$eval('#preview-chunks', el => el.textContent);
    const previewCost = await page.$eval('#preview-cost', el => el.textContent);
    
    // Verify the values
    expect(previewLength).toBe('50');
    expect(previewChunks).toBe('1');
    expect(parseFloat(previewCost)).toBeCloseTo(0.00075, 5);
  });
  
  test('Mock mode generation works for both short and long text', async () => {
    // Test with short text
    await testGenerationWithLength('This is a short test.', 1);
    
    // Test with long text (that requires chunking)
    const longText = 'This is a test sentence. '.repeat(200);
    await testGenerationWithLength(longText, 3);
  });
});

async function testGenerationWithLength(text, expectedChunks) {
  // Navigate to the page
  await page.goto('http://localhost:5001/');
  
  // Clear existing text (if any)
  await page.$eval('#text-input', el => el.value = '');
  
  // Enter text in the textarea
  await page.type('#text-input', text);
  
  // Enable mock mode
  await page.check('#mock-mode');
  
  // Select voice and model
  await page.select('#voice-select', 'alloy');
  await page.select('#model-select', 'tts-1');
  
  // Submit the form
  await Promise.all([
    page.click('#submit-btn'),
    page.waitForSelector('#processing-indicator[style*="display: block"]'),
    page.waitForResponse(response => response.url().includes('/generate'))
  ]);
  
  // Verify that the audio player appears
  await page.waitForSelector('#audio-player', { visible: true });
  
  // Check that the audio source exists
  const audioSrc = await page.$eval('#audio-player source', el => el.src);
  expect(audioSrc).toBeTruthy();
}
```

## Conclusion

Ensuring comprehensive testing coverage for the text-to-speech application requires special attention to:

1. **Chunking Logic**: Verify that long texts are properly divided into chunks
2. **Audio Stitching**: Ensure that multiple audio segments are correctly combined
3. **User Interactions**: Test the complete flow from text input to audio playback
4. **Cost Calculations**: Verify the accuracy of cost estimates for different text lengths and models
5. **Error Handling**: Test all error scenarios, including API failures and invalid inputs

The test cases outlined in this guide provide a foundation for comprehensive testing of the application's most critical functionality, with special focus on the audio stitching cases for both short and long texts. 