# Text-to-Speech Application Overview

## Project Structure

The Text-to-Speech application is a Flask-based web service that converts text to speech using the OpenAI API. The application is containerized using Docker for easy deployment and testing.

### Key Directories and Files

```
text-to-speech/
├── app.py                 # Main Flask application
├── generator.py           # Core text-to-speech functionality
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Example environment variables
├── .cursorrules           # Configuration for Cursor IDE
├── static/                # Static web assets
│   └── js/                # JavaScript files
│       └── main.js        # Client-side JavaScript
├── templates/             # HTML templates
│   ├── base.html          # Base template with common elements
│   ├── index.html         # Homepage template
│   ├── result.html        # Results page template
│   └── history.html       # History page template
├── output/                # Generated audio files
├── tests/                 # Server-side tests (Python)
│   ├── test_generator.py  # Tests for generator.py
│   ├── test_pdf_support.py # Tests for PDF functionality
│   ├── test_docker_web.py # Tests for web interface in Docker
│   └── test_docker_generation.py # Tests for speech generation in Docker
└── client-tests/          # Client-side tests (JavaScript)
    ├── main.test.js       # Tests for main.js functionality
    ├── pdf-support.test.js # Tests for PDF upload functionality
    └── setupTests.js      # Jest test setup
```

## Core Features

The application provides the following core features:

1. **Text-to-Speech Conversion**
   - Convert text to speech using OpenAI's TTS API
   - Support for multiple voices and models

2. **PDF Document Support**
   - Upload and extract text from PDF documents
   - Automatic text extraction using PyPDF2
   - History tracking of PDF sources

3. **Long Text Handling**
   - Automatic chunking of long texts
   - Audio stitching of multiple chunks

## Core Functionality

1. **Text Processing**: The application processes text input, handling large texts by splitting them into manageable chunks.
2. **API Integration**: It connects to OpenAI's Text-to-Speech API to convert text to audio.
3. **Audio Stitching**: For longer texts, it stitches together multiple audio segments.
4. **Cost Calculation**: It provides cost estimates based on text length and the selected model.
5. **Web Interface**: It offers a user-friendly interface for uploading text and generating speech.

## Testing Strategy

### Server-Side Testing (Python)

- **Unit Tests**: Tests for individual functions in generator.py.
- **Integration Tests**: Tests that verify the application's components work together correctly.
- **Docker Tests**: Tests that verify the application works correctly inside a Docker container.

### Client-Side Testing (JavaScript)

- **Unit Tests**: Tests for individual functions in main.js.
- **Coverage Tests**: Tests that measure code coverage to identify untested code paths.

### Manual Testing

- **Local Testing**: Running the application locally for development and testing.
- **Docker Testing**: Running the application in a Docker container to simulate production environment.

## Running the Tests

### Python Tests

```bash
# Run all Python tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_generator.py
```

### JavaScript Tests

```bash
# Run JavaScript tests
npm test

# Run JavaScript tests with coverage
npm run test:coverage
```

### Docker Tests

```bash
# Run tests against Docker container
./run_docker_tests.sh
```

### Client-Side Tests

```bash
# Run client-side tests
./run_client_tests.sh
```

## Key Testing Scenarios

1. **Text Input Handling**: Verify that the application correctly handles text inputs of various lengths.
2. **Cost Calculation**: Verify that cost estimates are calculated correctly based on text length and model.
3. **Audio Generation**: Verify that audio is generated correctly for different text inputs and voices.
4. **Audio Stitching**: Verify that audio stitching works correctly for longer texts.
5. **Error Handling**: Verify that the application handles errors gracefully (API errors, invalid inputs, etc.).

## Development Guidelines

1. **Code Style**: Follow PEP 8 guidelines for Python code and standard JavaScript style guidelines.
2. **Testing**: Write tests for all new features and ensure existing tests pass.
3. **Documentation**: Document new features and update existing documentation.
4. **Versioning**: Use semantic versioning for releases.
5. **Commits**: Use descriptive commit messages. 