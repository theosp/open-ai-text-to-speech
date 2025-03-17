# Text-to-Speech Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Python application that converts text to speech using OpenAI's Text-to-Speech API. Designed for handling texts of any size with automatic chunking and seamless audio stitching.

> 📌 **Repository**: [github.com/theosp/open-ai-text-to-speech](https://github.com/theosp/open-ai-text-to-speech)

## Sponsored by JustDo

This project's development was sponsored by [JustDo.com](https://justdo.com), a Source-Available enterprise-grade project management platform.

> *Every business is unique, and no single project management tool can meet everyone's needs. JustDo's source-availability lets you turn complexity into your competitive edge.*

Check out JustDo on GitHub: [github.com/justdoinc/justdo](https://github.com/justdoinc/justdo) - stars are highly appreciated 🙏

## Features

- Convert text from files to speech with high-quality results
- Direct PDF document support with automatic text extraction
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- Robust command-line interface with intuitive options
- Smart handling of large files with automatic chunking and stitching
- Cost estimation before processing to avoid surprises
- Comprehensive test suite with 100% client-side test coverage
- Advanced error handling with automatic retries
- Works with both standard and high-definition TTS models

## Prerequisites

- Python 3.7+
- FFmpeg (required for audio processing and stitching)
- OpenAI API key

## Getting Started

### 1. Install FFmpeg

**FFmpeg is required** for audio processing and file stitching. The application will not work properly without it.

#### macOS:
```bash
# Using Homebrew
brew install ffmpeg
```

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### Windows:
```bash
# Using Chocolatey
choco install ffmpeg

# Or using Scoop
scoop install ffmpeg
```

To verify installation:
```bash
ffmpeg -version
```

### 2. Clone and Setup the Repository

```bash
# Clone the repository
git clone https://github.com/theosp/open-ai-text-to-speech.git
cd open-ai-text-to-speech

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Your OpenAI API Key

You'll need an OpenAI API key to use the Text-to-Speech service. You can provide it in one of three ways:

1. As a command-line argument:
   ```bash
   python generator.py --api-key YOUR_API_KEY
   ```

2. As an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. In a `.env` file in the project directory:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Basic Usage

```bash
# Create an input.txt file with your text
echo "Hello, this is a test of the text to speech system." > input.txt

# Generate speech with default settings
python generator.py --api-key YOUR_OPENAI_API_KEY
```

### Advanced Options

```bash
# Use a different voice
python generator.py --api-key YOUR_API_KEY --voice nova

# Specify input and output files
python generator.py --api-key YOUR_API_KEY --input-file custom.txt --output-file custom.mp3

# Use a different model (higher quality)
python generator.py --api-key YOUR_API_KEY --model tts-1-hd

# Skip the confirmation prompt
python generator.py --api-key YOUR_API_KEY --force
```

### Large File Support

The application automatically handles large text files:

1. Text exceeding OpenAI's character limit (4096 characters) is split into smaller chunks
2. Each chunk is processed separately
3. The resulting audio files are stitched together seamlessly
4. The final audio file is saved to the specified output location

Before processing, you'll see information about:
- Text length
- Number of chunks required
- Estimated cost based on character count and model
- Option to confirm or cancel the operation

### Environment Variables

Instead of passing your API key as a command line argument, you can set it as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
python generator.py
```

Or use a `.env` file in the project directory:

```
OPENAI_API_KEY=your-api-key-here
```

## Pricing Information

The application calculates cost based on OpenAI's pricing:

- Standard model (tts-1): $0.015 per 1,000 characters
- High-definition model (tts-1-hd): $0.030 per 1,000 characters

You'll see the estimated cost before processing, giving you a chance to cancel if needed.

## Development and Testing

### Running Tests

This project has extensive test coverage for both server-side and client-side code.

#### Client-Side Tests

```bash
# Navigate to the project directory
cd text-to-speech

# Install npm dependencies if not already installed
npm install

# Run client-side tests
npm test
```

#### Server-Side Tests

```bash
# Run Python tests
pytest tests/

# Run tests with coverage report
pytest --cov=app --cov=generator --cov=utils
```

### Testing Documentation

For more detailed information about testing practices in this project, see:

- [Testing Guide](docs/instructions/testing_guide.md)
- [Client-Side Testing](docs/instructions/client_side_testing.md)
- [Server-Side Testing](docs/instructions/server_side_testing.md)

These guides include best practices for:
- Asynchronous testing
- DOM manipulation testing
- API mocking
- Proper test structure and organization

## Error Handling

The application handles various error scenarios:

- Missing API key
- Authentication errors
- Rate limiting
- Network timeouts
- File I/O errors
- Large file processing issues

## Contributing

Contributions are welcome! Here's how you can help improve this project:

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run the tests to ensure everything works**:
   ```bash
   python run_tests.py --coverage
   ```
5. **Submit a pull request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Maintain or improve code coverage (currently at 78%)
- Document new features in the README

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for their Text-to-Speech API
- FFmpeg project for audio processing capabilities
- Contributors to all the open source libraries used in this project

## Web Interface

In addition to the command-line tool, this project now includes a web interface built with Flask, making it easier to use the text-to-speech generation capabilities.

### Features

- User-friendly web interface for text input
- Support for all available voices and models
- Preview of estimated cost before processing
- Storage of generation history
- Audio playback, download, and management

### Environment Setup

The application requires an OpenAI API key to function. You can set this up in one of two ways:

1. Copy the example environment file and edit it:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

2. Export the environment variable directly:
   ```bash
   export OPENAI_API_KEY=your-api-key-here
   ```

### How to Run the Web Interface

#### Option 1: Using Docker (Recommended)

The easiest way to run the application is using Docker, which eliminates any dependency issues:

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

2. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY=your-api-key-here
   ```
   
   Or create a `.env` file in the project directory with the following content:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. Build and start the Docker container:
   ```bash
   # If using Docker Compose V2
   docker compose up -d
   
   # If using Docker Compose V1
   docker-compose up -d
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5001/
   ```

5. To stop the container:
   ```bash
   # If using Docker Compose V2
   docker compose down
   
   # If using Docker Compose V1
   docker-compose down
   ```

> **Note:** The Docker setup has been tested and works correctly. The application will be available on port 5001, and all generated files will be stored in the `output` directory, which is mounted as a volume in the container.

#### Option 2: Running Locally

If you prefer to run the application locally:

1. Make sure you have installed all the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your-api-key-here
   ```
   
   Or use a `.env` file in the project directory with the following content:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

3. Start the Flask application:
   ```
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5001/
   ```

### Using the Web Interface

1. Enter the text you want to convert to speech in the text area
2. Select your preferred voice and model
3. Click the "Preview Cost" button to see the estimated cost before proceeding
4. Click "Generate Speech" to convert your text to speech
5. When processing is complete, you'll be redirected to a results page where you can:
   - Play the generated audio
   - Download the MP3 file
   - View processing details
6. Visit the History page to access all your previously generated audio files

### File Storage

Generated audio files are stored in the `output` directory. The application maintains a history of all generations in a JSON file. 