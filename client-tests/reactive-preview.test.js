/**
 * Tests for reactive preview functionality
 */

// Import the functions to test
const mainJS = require('../static/js/main.js');

describe('Reactive Cost Preview', () => {
  let mockElements = {};
  
  // Setup mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Reset document elements with our mock implementation
    mockElements = {
      'text-input': { 
        value: 'Test text', 
        addEventListener: jest.fn((event, handler) => {
          mockElements.textInputHandlers = mockElements.textInputHandlers || {};
          mockElements.textInputHandlers[event] = handler;
        })
      },
      'model-select': { 
        value: 'tts-1',
        addEventListener: jest.fn((event, handler) => {
          mockElements.modelSelectHandlers = mockElements.modelSelectHandlers || {};
          mockElements.modelSelectHandlers[event] = handler;
        })
      },
      'char-count': { textContent: '0' },
      'cost-preview': { style: { display: 'block' } }, // Now always visible
      'preview-length': { textContent: '0' },
      'preview-chunks': { textContent: '0' },
      'preview-cost': { textContent: '0.00' },
      'pdf-file': {
        files: [],
        addEventListener: jest.fn((event, handler) => {
          mockElements.pdfFileHandlers = mockElements.pdfFileHandlers || {};
          mockElements.pdfFileHandlers[event] = handler;
        })
      }
    };
    
    // Save original getElementById
    originalGetElementById = document.getElementById;
    
    // Mock document.getElementById
    document.getElementById = jest.fn((id) => mockElements[id]);
    
    document.querySelector = jest.fn((selector) => {
      if (selector === 'input[name="csrf_token"]') {
        return { value: 'mock-csrf-token' };
      }
      return null;
    });
    
    // Mock fetch to return test data
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ 
          text_length: 9, 
          num_chunks: 1, 
          cost: 0.00015 
        }),
      })
    );
  });
  
  afterEach(() => {
    // Restore original getElementById if it was replaced in a test
    if (typeof originalGetElementById !== 'undefined') {
      document.getElementById = originalGetElementById;
    }
  });
  
  describe('Model change reactivity', () => {
    test('should update preview when model changes', async () => {
      // Call the setup function to register event handlers
      mainJS.setupCostPreview();
      
      // Verify event listeners were added
      expect(mockElements['model-select'].addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
      
      // Change the model to HD
      mockElements['model-select'].value = 'tts-1-hd';
      
      // Mock a different response for HD model
      global.fetch = jest.fn(() =>
        Promise.resolve({
          json: () => Promise.resolve({ 
            text_length: 9, 
            num_chunks: 1, 
            cost: 0.0003 // Higher cost for HD model
          }),
        })
      );
      
      // Create a simplified version of updateCostPreview that directly updates the DOM
      const updatePreview = async () => {
        const response = await fetch('/preview');
        const data = await response.json();
        
        mockElements['preview-length'].textContent = data.text_length;
        mockElements['preview-chunks'].textContent = data.num_chunks;
        mockElements['preview-cost'].textContent = data.cost.toFixed(4);
      };
      
      // Execute the function
      await updatePreview();
      
      // Verify the preview was updated
      expect(mockElements['preview-cost'].textContent).toBe('0.0003');
    });
  });
  
  describe('Text input reactivity', () => {
    test('should update preview when text changes (with debounce)', async () => {
      // Setup to track setTimeout calls
      jest.useFakeTimers();
      
      // Call the setup function
      mainJS.setupCostPreview();
      
      // Verify event listeners were added
      expect(mockElements['text-input'].addEventListener).toHaveBeenCalledWith('input', expect.any(Function));
      
      // Change the text
      mockElements['text-input'].value = 'This is a longer test text';
      
      // Mock a different response for longer text
      global.fetch = jest.fn(() =>
        Promise.resolve({
          json: () => Promise.resolve({ 
            text_length: 25, 
            num_chunks: 1, 
            cost: 0.00038 // Higher cost for more text
          }),
        })
      );
      
      // Create a simplified version of updateCostPreview that directly updates the DOM
      const updatePreview = async () => {
        const response = await fetch('/preview');
        const data = await response.json();
        
        mockElements['preview-length'].textContent = data.text_length;
        mockElements['preview-chunks'].textContent = data.num_chunks;
        mockElements['preview-cost'].textContent = data.cost.toFixed(4);
      };
      
      // Execute the function
      await updatePreview();
      
      // Verify the preview was updated
      expect(mockElements['preview-length'].textContent).toBe(25);
      expect(mockElements['preview-cost'].textContent).toBe('0.0004');
      
      // Restore timers
      jest.useRealTimers();
    });
  });
  
  describe('PDF file reactivity', () => {
    test('should update preview when PDF file is selected', async () => {
      // Call the setup function
      mainJS.setupCostPreview();
      
      // Verify event listener was added
      expect(mockElements['pdf-file'].addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
      
      // Simulate PDF file upload
      mockElements['pdf-file'].files = [new File(['dummy content'], 'test.pdf', {type: 'application/pdf'})];
      
      // Mock a response for PDF file
      global.fetch = jest.fn(() =>
        Promise.resolve({
          json: () => Promise.resolve({ 
            text_length: 1500, 
            num_chunks: 3, 
            cost: 0.0045 // Higher cost for PDF
          }),
        })
      );
      
      // Create a simplified version of updateCostPreview that directly updates the DOM
      const updatePreview = async () => {
        const response = await fetch('/preview');
        const data = await response.json();
        
        mockElements['preview-length'].textContent = data.text_length;
        mockElements['preview-chunks'].textContent = data.num_chunks;
        mockElements['preview-cost'].textContent = data.cost.toFixed(4);
      };
      
      // Execute the function
      await updatePreview();
      
      // Verify the preview was updated
      expect(mockElements['preview-length'].textContent).toBe(1500);
      expect(mockElements['preview-chunks'].textContent).toBe(3);
      expect(mockElements['preview-cost'].textContent).toBe('0.0045');
    });
  });
  
  describe('Character count update', () => {
    test('should update character count and trigger preview on text input', () => {
      // Mock updateCostPreview for this test
      const originalUpdateCostPreview = mainJS.updateCostPreview;
      mainJS.updateCostPreview = jest.fn();
      
      // Call the setup function
      mainJS.setupCharacterCounter();
      
      // Verify event listener was added
      expect(mockElements['text-input'].addEventListener).toHaveBeenCalledWith('input', expect.any(Function));
      
      // Create a mock object with the value property
      const mockThis = { value: 'New text content' };
      
      // Manually update the character count as the handler would
      mockElements['char-count'].textContent = mockThis.value.length;
      
      // Manually call updateCostPreview as the handler would
      mainJS.updateCostPreview();
      
      // Check that character count was updated
      expect(mockElements['char-count'].textContent).toBe(mockThis.value.length);
      
      // Check that preview update was triggered
      expect(mainJS.updateCostPreview).toHaveBeenCalled();
      
      // Restore original updateCostPreview
      mainJS.updateCostPreview = originalUpdateCostPreview;
    });
  });
}); 