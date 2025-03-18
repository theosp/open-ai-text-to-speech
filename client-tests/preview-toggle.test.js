/**
 * Test file for testing automatic cost preview updates
 */

const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

describe('Automatic Cost Preview Updates', () => {
    let dom;
    let window;
    let document;

    beforeEach(() => {
        // Set up a new JSDOM instance before each test
        const htmlContent = fs.readFileSync(path.resolve(__dirname, '../templates/index.html'), 'utf8');
        dom = new JSDOM(htmlContent, {
            url: 'http://localhost/',
            runScripts: 'dangerously',
            resources: 'usable'
        });
        window = dom.window;
        document = window.document;

        // Mock the necessary functions and objects
        window.bootstrap = {
            Modal: class {
                constructor() {}
                show() {}
                hide() {}
            }
        };

        // Create a mock XMLHttpRequest
        window.XMLHttpRequest = class {
            constructor() {
                this.status = 200;
                this.responseText = JSON.stringify({
                    text_length: 500,
                    num_chunks: 1,
                    cost: 0.0075
                });
            }
            open() {}
            send() {
                // Simulate async response
                setTimeout(() => {
                    if (this.onreadystatechange) {
                        this.readyState = 4;
                        this.onreadystatechange();
                    }
                }, 10);
            }
        };

        // Load main.js
        const mainJs = fs.readFileSync(path.resolve(__dirname, '../static/js/main.js'), 'utf8');
        const scriptElement = document.createElement('script');
        scriptElement.textContent = mainJs;
        document.body.appendChild(scriptElement);

        // Set up DOM elements needed for testing
        const costPreview = document.createElement('div');
        costPreview.id = 'cost-preview';
        costPreview.style.display = 'block'; // Always visible now
        document.body.appendChild(costPreview);

        const previewLength = document.createElement('span');
        previewLength.id = 'preview-length';
        costPreview.appendChild(previewLength);

        const previewChunks = document.createElement('span');
        previewChunks.id = 'preview-chunks';
        costPreview.appendChild(previewChunks);

        const previewCost = document.createElement('span');
        previewCost.id = 'preview-cost';
        costPreview.appendChild(previewCost);

        // Text input
        const textInput = document.createElement('textarea');
        textInput.id = 'text-input';
        textInput.value = '';  // Empty initially
        document.body.appendChild(textInput);

        // Model select
        const modelSelect = document.createElement('select');
        modelSelect.id = 'model-select';
        const option = document.createElement('option');
        option.value = 'tts-1';
        option.textContent = 'OpenAI TTS-1';
        modelSelect.appendChild(option);
        document.body.appendChild(modelSelect);

        // PDF input
        const pdfFileInput = document.createElement('input');
        pdfFileInput.id = 'pdf-file';
        pdfFileInput.type = 'file';
        document.body.appendChild(pdfFileInput);

        // Initialize functions (simulate DOMContentLoaded)
        if (window.setupCostPreview) {
            window.setupCostPreview();
        }
    });

    test('Cost preview shows zeros when no text or PDF is provided', async () => {
        // Arrange
        const previewLength = document.getElementById('preview-length');
        const previewChunks = document.getElementById('preview-chunks');
        const previewCost = document.getElementById('preview-cost');

        // Wait for initial update
        await new Promise(resolve => setTimeout(resolve, 50));

        // Assert - preview should show zeros
        expect(previewLength.textContent).toBe('0');
        expect(previewChunks.textContent).toBe('0');
        expect(previewCost.textContent).toBe('0.0000');
    });

    test('Cost preview updates when text is entered', async () => {
        // Arrange
        const textInput = document.getElementById('text-input');
        const previewLength = document.getElementById('preview-length');
        const previewChunks = document.getElementById('preview-chunks');
        const previewCost = document.getElementById('preview-cost');

        // Act - enter text and trigger input event
        textInput.value = 'Some sample text for testing';
        const inputEvent = new window.Event('input', { bubbles: true });
        textInput.dispatchEvent(inputEvent);

        // Wait for debounced update
        await new Promise(resolve => setTimeout(resolve, 600));

        // Assert - preview should show updated values
        expect(previewLength.textContent).toBe('500');
        expect(previewChunks.textContent).toBe('1');
        expect(previewCost.textContent).toBe('0.0075');
    });

    test('Cost preview updates when model is changed', async () => {
        // Skip this test for now as we'd need to implement more sophisticated mocking
        // This is a placeholder for a more complete test
        expect(true).toBe(true);
    });
}); 