# Voice Sample Feature: Manual Test Plan

## Feature Overview
The voice sample feature allows users to hear a sample of each voice before selecting it for text-to-speech conversion. When a user clicks on a voice in the "Available Voices" section, the application plays a short audio sample of that voice, provides visual feedback, and updates the voice selection dropdown.

## Prerequisites
1. The application is running locally at http://127.0.0.1:5000
2. Sample MP3 files exist in the `static/audio/samples` directory (one for each voice)
3. Browser supports HTML5 audio playback

## Test Cases

### 1. Basic Voice Sample Playback
**Steps:**
1. Navigate to the home page (http://127.0.0.1:5000)
2. Click on the "Alloy" voice in the Available Voices section
3. Observe behavior

**Expected Results:**
- An audio sample should play (if audio files exist)
- The "Alloy" voice option should be highlighted with a purple background
- The play icon should pulse while audio is playing
- The voice dropdown should be updated to select "Alloy"

### 2. Stopping Playback
**Steps:**
1. Click on "Alloy" voice to start playback
2. Click on "Alloy" voice again while it's playing

**Expected Results:**
- The audio playback should stop
- The highlighting should be removed
- The play icon should stop pulsing

### 3. Switching Between Voices
**Steps:**
1. Click on "Alloy" voice to start playback
2. While it's playing, click on "Echo" voice

**Expected Results:**
- The "Alloy" audio should stop
- The "Echo" audio should start playing
- The highlight should move from "Alloy" to "Echo"
- The voice dropdown should update to "Echo"

### 4. Completing Playback
**Steps:**
1. Click on "Alloy" voice
2. Let the audio sample play to completion (don't interrupt)

**Expected Results:**
- When the audio finishes, the highlight should be removed automatically
- The play icon should stop pulsing
- The voice dropdown should remain set to "Alloy"

### 5. Error Handling
**Steps:**
1. Temporarily rename or remove a sample audio file (e.g., rename "alloy.mp3")
2. Click on the corresponding voice option

**Expected Results:**
- No audio should play
- The UI should gracefully handle the error (no console errors)
- The voice dropdown should still update correctly

### 6. Mobile Responsiveness
**Steps:**
1. Open the application on a mobile device or use browser developer tools to simulate mobile view
2. Click on voice options

**Expected Results:**
- The voice options layout should adjust for smaller screens
- The click functionality should work the same as on desktop

## Sample Generation Tests

### 1. Sample Generation Route Access
**Steps:**
1. Navigate to http://127.0.0.1:5000/generate-voice-samples without setting the ALLOW_SAMPLE_GENERATION environment variable

**Expected Results:**
- Access should be restricted
- User should be redirected to the home page with a "Sample generation is disabled" message

### 2. Sample Generation (Admin Only)
**Steps:**
1. Stop the application
2. Set environment variable: `export ALLOW_SAMPLE_GENERATION=true`
3. Restart the application
4. Navigate to http://127.0.0.1:5000/generate-voice-samples

**Expected Results:**
- If OpenAI API key is valid, sample files should be generated
- User should see success messages for each voice
- Audio samples should appear in the static/audio/samples directory

## Verification
After completing these tests, verify that:
1. Users can easily preview voice samples
2. The UI provides clear visual feedback during playback
3. The voice selection is synchronized with the preview
4. The feature works across different browsers and devices 