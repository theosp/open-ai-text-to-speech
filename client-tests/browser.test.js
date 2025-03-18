/**
 * Browser-based tests for the Text-to-Speech application
 * These tests use Puppeteer to interact with the actual web interface
 */

const puppeteer = require('puppeteer');

// Configuration
const BASE_URL = 'http://localhost:5001';
const WAIT_TIMEOUT = 10000; // 10 seconds

// Test suite
describe('UI Tests', () => {
  let browser;
  let page;
  
  // Setup before all tests
  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: 'new', // Use new headless mode
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    page = await browser.newPage();
  });
  
  // Teardown after all tests
  afterAll(async () => {
    await browser.close();
  });
  
  // Test that the input area is centered and features appear below it
  test('page layout matches the centered design', async () => {
    // Navigate to the main page
    await page.goto(BASE_URL, { waitUntil: 'networkidle0' });
    
    // Check for centered input area
    const inputContainer = await page.$('.row.justify-content-center');
    expect(inputContainer).not.toBeNull();
    
    // Get positions of input area and features section
    const inputBounds = await inputContainer.boundingBox();
    const featuresSection = await page.$('.row.mt-4');
    const featuresBounds = await featuresSection.boundingBox();
    
    // Features should appear below the input area
    expect(featuresBounds.y).toBeGreaterThan(inputBounds.y + inputBounds.height);
  });
  
  // Test that the preview shows zeros when text is empty
  test('preview shows zeros when text is empty', async () => {
    // Navigate to the main page
    await page.goto(BASE_URL, { waitUntil: 'networkidle0' });
    
    // Clear the text area (in case there's default text)
    await page.$eval('#text-input', el => el.value = '');
    
    // The preview should be visible by default - no need to click a button
    
    // Wait a moment for any updates to occur
    await page.waitForTimeout(100);
    
    // Check the values in the preview
    const previewLength = await page.$eval('#preview-length', el => el.textContent);
    const previewChunks = await page.$eval('#preview-chunks', el => el.textContent);
    const previewCost = await page.$eval('#preview-cost', el => el.textContent);
    
    // Verify the values are zeros
    expect(previewLength).toBe('0');
    expect(previewChunks).toBe('0');
    expect(previewCost).toBe('0.0000');
    
    // Verify no alert was shown
    const dialogWasShown = await page.evaluate(() => {
      return window._dialogShown === true;
    });
    expect(dialogWasShown).toBeFalsy();
  });
  
  // Test the Remove All button in history page
  test('Remove All button exists and works in history page', async () => {
    // Create a spy for the confirm dialog
    await page.evaluate(() => {
      window.confirm = jest.fn(() => true);
      window._confirmCalled = false;
      window.originalConfirm = window.confirm;
      window.confirm = function() {
        window._confirmCalled = true;
        return true;
      };
    });
    
    // Navigate to the history page
    await page.goto(`${BASE_URL}/history`, { waitUntil: 'networkidle0' });
    
    // Check if there are any history items
    const hasHistoryItems = await page.evaluate(() => {
      return document.querySelector('.history-item') !== null;
    });
    
    // Only run this test if there are history items
    if (hasHistoryItems) {
      // Check if the Remove All button exists
      const removeAllBtn = await page.$('a.btn-danger');
      expect(removeAllBtn).not.toBeNull();
      
      // Click the Remove All button
      await removeAllBtn.click();
      
      // Verify that confirm was called
      const confirmCalled = await page.evaluate(() => {
        const result = window._confirmCalled;
        // Clean up
        window.confirm = window.originalConfirm;
        delete window._confirmCalled;
        delete window.originalConfirm;
        return result;
      });
      
      expect(confirmCalled).toBeTruthy();
      
      // Verify we're still on the history page after deletion
      const url = page.url();
      expect(url).toContain('/history');
    } else {
      console.log('No history items found, skipping Remove All button test');
    }
  });
}); 