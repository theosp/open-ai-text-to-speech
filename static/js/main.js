/**
 * Main JavaScript functionality for Text-to-Speech application
 */

// Set current year for copyright
function setCurrentYear() {
    const currentYearElement = document.getElementById('current-year');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }
}

// Update character count
function setupCharacterCounter() {
    const textInput = document.getElementById('text-input');
    const charCount = document.getElementById('char-count');
    
    if (textInput && charCount) {
        // Update count on input
        textInput.addEventListener('input', function() {
            charCount.textContent = this.value.length;
            
            // Trigger preview update if there's text
            if (this.value.length > 0) {
                updateCostPreview();
            }
        });
        
        // Initialize character count
        charCount.textContent = textInput.value.length;
    }
}

// Helper function to update cost preview
function updateCostPreview() {
    const textInput = document.getElementById('text-input');
    const modelSelect = document.getElementById('model-select');
    const pdfFileInput = document.getElementById('pdf-file');
    const costPreview = document.getElementById('cost-preview');
    const previewLength = document.getElementById('preview-length');
    const previewChunks = document.getElementById('preview-chunks');
    const previewCost = document.getElementById('preview-cost');
    
    console.log('updateCostPreview called');
    
    if (!modelSelect || !costPreview || 
        !previewLength || !previewChunks || !previewCost) {
        console.log('Missing required elements');
        return;
    }
    
    const text = textInput ? textInput.value : '';
    const model = modelSelect.value;
    const hasPdf = pdfFileInput && pdfFileInput.files && pdfFileInput.files.length > 0;
    
    console.log('Text length:', text.length);
    console.log('Model:', model);
    console.log('Has PDF:', hasPdf);
    if (hasPdf) {
        console.log('PDF file name:', pdfFileInput.files[0].name);
        console.log('PDF file size:', pdfFileInput.files[0].size);
    }
    
    // If there's no text and no PDF file, exit early
    if (text.length === 0 && !hasPdf) {
        console.log('No text and no PDF, exiting early');
        return;
    }
    
    // If we have a PDF file, we need to use FormData to send it
    if (hasPdf) {
        console.log('Sending PDF file to server');
        const formData = new FormData();
        formData.append('pdf_file', pdfFileInput.files[0]);
        formData.append('model', model);
        if (text.length > 0) {
            console.log('Also sending text with PDF');
            formData.append('text', text);
        }
        
        console.log('FormData created:', formData);
        
        fetch('/preview', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.error) {
                console.error('Error from server:', data.error);
                return;
            }
            
            previewLength.textContent = data.text_length;
            previewChunks.textContent = data.num_chunks;
            previewCost.textContent = data.cost.toFixed(4);
            // Don't set display here
            // costPreview.style.display = 'block';
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    } else {
        // Use the existing URLSearchParams approach for text input
        console.log('Sending text only to server');
        fetch('/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: new URLSearchParams({
                'text': text,
                'model': model
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.error) {
                console.error('Error from server:', data.error);
                return;
            }
            
            previewLength.textContent = data.text_length;
            previewChunks.textContent = data.num_chunks;
            previewCost.textContent = data.cost.toFixed(4);
            // Don't set display here
            // costPreview.style.display = 'block';
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    }
}

// Preview cost
function setupCostPreview() {
    const previewBtn = document.getElementById('preview-btn');
    const textInput = document.getElementById('text-input');
    const pdfFileInput = document.getElementById('pdf-file');
    const modelSelect = document.getElementById('model-select');
    const costPreview = document.getElementById('cost-preview');
    const previewLength = document.getElementById('preview-length');
    const previewChunks = document.getElementById('preview-chunks');
    const previewCost = document.getElementById('preview-cost');
    
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            // If preview is already showing, toggle it off
            if (costPreview.style.display === 'block') {
                costPreview.style.display = 'none';
                return;
            }
            
            const text = textInput ? textInput.value : '';
            const hasPdf = pdfFileInput && pdfFileInput.files && pdfFileInput.files.length > 0;
            
            if (text.length === 0 && !hasPdf) {
                // Instead of showing an alert, display the preview with zeros
                previewLength.textContent = '0';
                previewChunks.textContent = '0';
                previewCost.textContent = '0.0000';
                costPreview.style.display = 'block';
                return;
            }
            
            updateCostPreview();
        });
    }
    
    // Make preview reactive to model changes
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            const hasPdf = pdfFileInput && pdfFileInput.files && pdfFileInput.files.length > 0;
            const hasText = textInput && textInput.value.length > 0;
            
            if (hasText || hasPdf) {
                updateCostPreview();
            } else if (costPreview) {
                // Also handle empty case on model change if preview is already visible
                if (costPreview.style.display === 'block') {
                    previewLength.textContent = '0';
                    previewChunks.textContent = '0';
                    previewCost.textContent = '0.0000';
                }
            }
        });
    }
    
    // Add a debounced text input handler for reactivity
    if (textInput) {
        let debounceTimeout;
        textInput.addEventListener('input', function() {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                if (this.value.length > 0) {
                    updateCostPreview();
                } else if (costPreview && costPreview.style.display === 'block') {
                    // Handle case when user deletes all text
                    const hasPdf = pdfFileInput && pdfFileInput.files && pdfFileInput.files.length > 0;
                    if (!hasPdf) {
                        previewLength.textContent = '0';
                        previewChunks.textContent = '0';
                        previewCost.textContent = '0.0000';
                    }
                }
            }, 500); // 500ms debounce
        });
    }
    
    // Add PDF file input change handler
    if (pdfFileInput) {
        pdfFileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                updateCostPreview();
            }
        });
    }
    
    // Add clear button handler for PDF
    const clearFileBtn = document.getElementById('clear-file-btn');
    if (clearFileBtn && pdfFileInput) {
        clearFileBtn.addEventListener('click', function() {
            pdfFileInput.value = '';
            // If there's no text either and preview is showing, update with zeros
            if ((!textInput || textInput.value.length === 0) && costPreview && costPreview.style.display === 'block') {
                previewLength.textContent = '0';
                previewChunks.textContent = '0';
                previewCost.textContent = '0.0000';
            }
        });
    }
}

// Show processing indicator when form is submitted
function setupProcessingIndicator() {
    const form = document.getElementById('tts-form');
    const processingIndicator = document.getElementById('processing-indicator');
    const submitBtn = document.getElementById('submit-btn');
    
    if (form && processingIndicator && submitBtn) {
        form.addEventListener('submit', function() {
            processingIndicator.style.display = 'block';
            submitBtn.disabled = true;
        });
    }
}

// Setup voice sample playback
function setupVoiceSamples() {
    const voiceOptions = document.querySelectorAll('.voice-option');
    
    voiceOptions.forEach(option => {
        option.addEventListener('click', function() {
            const voiceName = this.dataset.voice;
            const isPlaying = this.classList.contains('playing');
            
            // Reset all voice options
            voiceOptions.forEach(opt => opt.classList.remove('playing'));
            
            // If this wasn't playing, play it now
            if (!isPlaying) {
                this.classList.add('playing');
                playVoiceSample(voiceName, this);
            } else {
                // Stop the audio if it was already playing
                const currentAudio = document.querySelector('.voice-sample-audio');
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio.remove();
                }
            }
            
            // Also update voice select dropdown
            const voiceSelect = document.getElementById('voice-select');
            if (voiceSelect) {
                voiceSelect.value = voiceName;
            }
        });
    });
}

// Play voice sample audio
function playVoiceSample(voice, voiceElement) {
    // Stop any currently playing audio
    const currentAudio = document.querySelector('.voice-sample-audio');
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.remove();
    }
    
    // Create and play new audio element
    const audio = new Audio(`/static/audio/samples/${voice}.mp3`);
    audio.className = 'voice-sample-audio';
    document.body.appendChild(audio);
    
    // Play the audio
    audio.play().catch(error => {
        console.error('Error playing voice sample:', error);
        if (voiceElement) {
            voiceElement.classList.remove('playing');
        }
    });
    
    // Remove playing class when audio ends
    audio.addEventListener('ended', () => {
        if (voiceElement) {
            voiceElement.classList.remove('playing');
        }
        audio.remove();
    });
}

// Initialize all functionality
function initApp() {
    setCurrentYear();
    setupCharacterCounter();
    setupCostPreview();
    setupProcessingIndicator();
    setupVoiceSamples();
}

// Run initialization when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        setCurrentYear,
        setupCharacterCounter,
        setupCostPreview,
        updateCostPreview,
        setupProcessingIndicator,
        setupVoiceSamples,
        playVoiceSample,
        initApp
    };
} 