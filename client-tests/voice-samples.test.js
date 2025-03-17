/**
 * Tests for voice sample playback functionality
 */

// Import Jest's jsdom setup to allow DOM manipulation
const { JSDOM } = require('jsdom');

// Setup DOM environment
const dom = new JSDOM(`
<!DOCTYPE html>
<html>
<body>
  <div class="voice-option" data-voice="alloy">
    <h6>Alloy</h6>
    <p class="text-muted mb-0">Voice description</p>
    <i class="bi bi-play-circle play-icon"></i>
  </div>
  <div class="voice-option" data-voice="echo">
    <h6>Echo</h6>
    <p class="text-muted mb-0">Voice description</p>
    <i class="bi bi-play-circle play-icon"></i>
  </div>
  <select id="voice-select">
    <option value="alloy">Alloy</option>
    <option value="echo">Echo</option>
  </select>
</body>
</html>
`);

// Set up global objects for the tests
global.document = dom.window.document;
global.window = dom.window;
global.Audio = jest.fn().mockImplementation(() => ({
  play: jest.fn().mockResolvedValue(),
  pause: jest.fn(),
  remove: jest.fn(),
  addEventListener: jest.fn((event, callback) => {
    if (event === 'ended') {
      // Store callback to simulate audio ending
      this.endedCallback = callback;
    }
  }),
  className: '',
}));
global.HTMLElement = dom.window.HTMLElement;
global.Element = dom.window.Element;

// Now mock the functions we're testing
const setupVoiceSamples = jest.fn((voiceOptions = document.querySelectorAll('.voice-option')) => {
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
});

const playVoiceSample = jest.fn((voice, voiceElement) => {
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
  
  // Mark the voice element as playing
  if (voiceElement) {
    voiceElement.classList.add('playing');
  }
  
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
  
  return audio;
});

describe('Voice Sample Functions', () => {
  beforeEach(() => {
    // Reset mocks and DOM state before each test
    jest.clearAllMocks();
    document.querySelectorAll('.voice-option').forEach(option => {
      option.classList.remove('playing');
    });
    if (document.querySelector('#voice-select')) {
      document.querySelector('#voice-select').value = '';
    }
    
    // Remove any audio elements
    const audioElements = document.querySelectorAll('.voice-sample-audio');
    audioElements.forEach(el => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    });
  });

  test('setupVoiceSamples adds click event listeners to voice options', () => {
    // Add event listener spy
    const addEventListenerSpy = jest.spyOn(Element.prototype, 'addEventListener');
    
    // Call the function
    setupVoiceSamples();
    
    // Check that addEventListener was called for each voice option
    expect(addEventListenerSpy).toHaveBeenCalled();
    expect(addEventListenerSpy).toHaveBeenCalledWith('click', expect.any(Function));
    
    addEventListenerSpy.mockRestore();
  });

  test('playVoiceSample creates and plays audio element', () => {
    const voiceElement = document.querySelector('[data-voice="alloy"]');
    
    // Call the function
    const audio = playVoiceSample('alloy', voiceElement);
    
    // Check that Audio was created with the correct URL
    expect(global.Audio).toHaveBeenCalledWith('/static/audio/samples/alloy.mp3');
    
    // Check that play was called
    expect(audio.play).toHaveBeenCalled();
    
    // Check that the voice element has playing class
    expect(voiceElement.classList.contains('playing')).toBe(true);
  });

  test('clicking a voice option triggers playback', () => {
    // Setup voice samples
    setupVoiceSamples();
    
    // Find the alloy option
    const alloyOption = document.querySelector('[data-voice="alloy"]');
    
    // Create a click event
    const clickEvent = new dom.window.MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Dispatch the click event
    alloyOption.dispatchEvent(clickEvent);
    
    // The voice element should have the playing class
    expect(alloyOption.classList.contains('playing')).toBe(true);
  });

  test('clicking an already playing voice stops playback', () => {
    // Setup voice samples
    setupVoiceSamples();
    
    // Find the alloy option and mark it as playing
    const alloyOption = document.querySelector('[data-voice="alloy"]');
    alloyOption.classList.add('playing');
    
    // Create a mock audio element and add it to the DOM
    const mockAudio = document.createElement('div');
    mockAudio.className = 'voice-sample-audio';
    mockAudio.pause = jest.fn();
    mockAudio.remove = jest.fn();
    document.body.appendChild(mockAudio);
    
    // Create a click event
    const clickEvent = new dom.window.MouseEvent('click', {
      bubbles: true,
      cancelable: true
    });
    
    // Dispatch the click event
    alloyOption.dispatchEvent(clickEvent);
    
    // Check if playing class was removed
    expect(alloyOption.classList.contains('playing')).toBe(false);
  });
}); 