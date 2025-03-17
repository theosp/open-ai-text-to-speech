/**
 * Test file for testing the Preview Cost button toggle functionality
 */

const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

describe('Preview Cost Button Toggle Functionality', () => {
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
        const previewBtn = document.createElement('button');
        previewBtn.id = 'preview-btn';
        previewBtn.textContent = 'Preview Cost';
        document.body.appendChild(previewBtn);

        const costPreview = document.createElement('div');
        costPreview.id = 'cost-preview';
        costPreview.style.display = 'none';
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
        textInput.value = 'Some sample text for testing';
        document.body.appendChild(textInput);

        // Model select
        const modelSelect = document.createElement('select');
        modelSelect.id = 'model-select';
        document.body.appendChild(modelSelect);

        // Initialize functions (simulate DOMContentLoaded)
        if (window.setupCostPreview) {
            window.setupCostPreview();
        }
    });

    test('Preview Cost button shows the cost preview when clicked', async () => {
        // Arrange
        const previewBtn = document.getElementById('preview-btn');
        const costPreview = document.getElementById('cost-preview');

        // Initial state - preview should be hidden
        expect(costPreview.style.display).toBe('none');

        // Act - click preview button
        previewBtn.click();

        // Assert - preview should now be shown
        await new Promise(resolve => setTimeout(resolve, 50)); // Wait for the async XMLHttpRequest mock
        expect(costPreview.style.display).toBe('block');
    });

    test('Preview Cost button toggles the cost preview when clicked again', async () => {
        // Arrange
        const previewBtn = document.getElementById('preview-btn');
        const costPreview = document.getElementById('cost-preview');

        // Initial state - preview should be hidden
        expect(costPreview.style.display).toBe('none');

        // Act - click preview button to show it
        previewBtn.click();
        await new Promise(resolve => setTimeout(resolve, 50)); // Wait for the async XMLHttpRequest mock
        
        // Assert - preview should now be shown
        expect(costPreview.style.display).toBe('block');
        
        // Act again - click preview button to hide it
        previewBtn.click();
        await new Promise(resolve => setTimeout(resolve, 50));
        
        // Assert - preview should be hidden again
        expect(costPreview.style.display).toBe('none');
    });

    test('Preview Cost button correctly toggles multiple times', async () => {
        // Arrange
        const previewBtn = document.getElementById('preview-btn');
        const costPreview = document.getElementById('cost-preview');

        // Act & Assert - Toggle multiple times
        for (let i = 0; i < 3; i++) {
            // Click to show
            previewBtn.click();
            await new Promise(resolve => setTimeout(resolve, 50));
            expect(costPreview.style.display).toBe('block');
            
            // Click to hide
            previewBtn.click();
            await new Promise(resolve => setTimeout(resolve, 50));
            expect(costPreview.style.display).toBe('none');
        }
    });
}); 