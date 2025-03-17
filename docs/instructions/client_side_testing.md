# Client-Side Testing Guide

This document provides detailed guidance on writing and running client-side tests for the Text-to-Speech application.

## Client-Side Test Structure

The client-side tests are located in the `client-tests` directory and use Jest as the testing framework.

### Key Files

- `client-tests/main.test.js`: Unit tests for the main JavaScript file.
- `client-tests/setupTests.js`: Setup file for Jest tests.
- `client-tests/browser.test.js`: Browser-based tests using Puppeteer.
- `static/js/main.js`: The JavaScript file being tested.

## Running the Tests

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run all client-side tests (including browser tests)
./run_client_tests.sh
```

## Coverage Reports

Test coverage reports are generated in the `client-tests/coverage` directory. The reports include:

- HTML report (view in a browser): `client-tests/coverage/lcov-report/index.html`
- XML report (for CI/CD): `client-tests/coverage/clover.xml`
- JSON report: `client-tests/coverage/coverage-final.json`

## Writing Tests

### Unit Tests

Unit tests for JavaScript functions should:

1. Mock DOM elements using `document.getElementById`.
2. Mock event listeners.
3. Mock fetch requests.
4. Assert expected behavior.

Example:

```javascript
test('setCurrentYear sets the current year', () => {
  // Mock DOM element
  const mockElement = { textContent: '' };
  document.getElementById.mockReturnValue(mockElement);
  
  // Call the function
  setCurrentYear();
  
  // Assert the expected behavior
  expect(document.getElementById).toHaveBeenCalledWith('current-year');
  expect(mockElement.textContent).toBe(new Date().getFullYear().toString());
});
```

### Browser Tests

Browser tests use Puppeteer to interact with the actual web interface:

1. Launch a headless browser with Puppeteer.
2. Navigate to the application URL.
3. Interact with the page (click buttons, fill forms, etc.).
4. Assert expected behavior.

Example:

```javascript
test('character counter updates when text is entered', async () => {
  // Navigate to the page
  await page.goto('http://localhost:5001/');
  
  // Enter text in the textarea
  await page.type('#text-input', 'Hello, world!');
  
  // Wait for the counter to update
  await page.waitForSelector('#char-count');
  
  // Get the counter value
  const counterValue = await page.$eval('#char-count', el => el.textContent);
  
  // Assert the expected behavior
  expect(counterValue).toBe('13');
});
```

## Required Test Cases

### 1. Text Input and Character Count

- Test that the character counter updates when text is entered.
- Test that the character count is initialized correctly when the page loads.

### 2. Cost Preview

- Test that the cost preview button shows the cost preview div.
- Test that the cost preview is calculated correctly based on text length and model.
- Test that an alert is shown if no text is entered.

### 3. Form Validation

- Test that the form validates required fields.
- Test that the form submits successfully with valid input.
- Test that the form shows appropriate error messages for invalid input.

### 4. Processing Indicator

- Test that the processing indicator is shown when the form is submitted.
- Test that the processing indicator is hidden after the form is processed.

### 5. Voice and Model Selection

- Test that different voices can be selected.
- Test that different models (standard, high-definition) can be selected.
- Test that the cost calculation updates when the model is changed.

### 6. Specific Text-to-Speech Scenarios

#### Case 1: Short Text (No Stitching)

1. Enter a short text (less than 3000 characters).
2. Verify the character count.
3. Check the cost preview.
4. Submit the form.
5. Verify the audio is generated (mock mode).

#### Case 2: Long Text (Stitching Required)

1. Enter a long text (more than 3000 characters).
2. Verify the character count.
3. Check the cost preview (should indicate multiple chunks).
4. Submit the form.
5. Verify the audio is generated and stitched together (mock mode).

## Test Mocking

To avoid actual API calls during testing, use the mock mode:

```javascript
// Mock the fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({
      text_length: 13,
      num_chunks: 1,
      cost: 0.00015
    })
  })
);

// Test the cost preview
test('cost preview shows correct values', async () => {
  // ... test implementation ...
});
```

For browser tests, use the mock_mode parameter:

```javascript
// Click the generate button with mock mode
await page.evaluate(() => {
  document.querySelector('#mock-mode').checked = true;
  document.querySelector('#tts-form').submit();
});
```

## Best Practices

1. **Isolation**: Each test should be independent of others.
2. **Mocking**: Avoid actual API calls by mocking.
3. **Selectors**: Use consistent selectors (IDs, classes) for DOM elements.
4. **Waits**: Use explicit waits in browser tests to ensure elements are ready.
5. **Assertions**: Make specific assertions about expected behavior.
6. **Coverage**: Aim for high test coverage of client-side code.
7. **Performance**: Keep tests fast to enable frequent execution.

## Asynchronous Testing Best Practices

When testing code that involves asynchronous operations (like fetch calls or event handlers with timeouts), follow these guidelines:

### 1. Use Async/Await

Always use async/await when testing asynchronous code:

```javascript
test('should fetch data and update the UI', async () => {
  // Setup mocks
  // ...
  
  // Execute async function
  await updateCostPreview();
  
  // Assert results
  expect(mockCostPreview.style.display).toBe('block');
});
```

### 2. Properly Mock Fetch Responses

Mock fetch responses to return promises that resolve with the expected data:

```javascript
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({
      text_length: 25,
      num_chunks: 1,
      cost: 0.00038
    })
  })
);
```

### 3. Wait for DOM Updates

When testing code that updates the DOM, ensure you wait for the updates to complete:

```javascript
// For browser tests with Puppeteer
await page.waitForSelector('#cost-preview[style*="display: block"]');

// For Jest tests, use await with the function that updates the DOM
await updateUIFunction();
```

### 4. Test Error Handling

Always test how your code handles errors in asynchronous operations:

```javascript
test('should handle fetch errors gracefully', async () => {
  // Mock fetch to reject
  global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));
  
  // Mock console.error
  console.error = jest.fn();
  
  // Call function that uses fetch
  await updateCostPreview();
  
  // Verify error was handled
  expect(console.error).toHaveBeenCalledWith('Error:', expect.any(Error));
});
```

### 5. Clean Up After Tests

Always restore original functions and mocks after each test:

```javascript
afterEach(() => {
  // Restore fetch
  global.fetch.mockRestore();
  
  // Restore console.error if it was mocked
  if (console.error.mockRestore) {
    console.error.mockRestore();
  }
});
```

### 6. Handle Debounced Functions

When testing functions that use debouncing or throttling:

```javascript
// Mock timers
jest.useFakeTimers();

// Trigger the debounced function
element.dispatchEvent(new Event('input'));

// Fast-forward timers
jest.advanceTimersByTime(300); // Advance by debounce delay

// Restore timers when done
jest.useRealTimers();
```

### 7. Simplify Complex Functions for Testing

For complex asynchronous functions, consider creating simplified versions for testing that maintain the core functionality:

```javascript
// Original complex function with multiple dependencies
function updateUI() { /* complex implementation */ }

// Simplified version for testing
const testUpdateUI = async () => {
  const response = await fetch('/api/data');
  const data = await response.json();
  document.getElementById('result').textContent = data.result;
};
```

Following these practices will ensure your asynchronous tests are reliable, maintainable, and accurately reflect your code's behavior. 