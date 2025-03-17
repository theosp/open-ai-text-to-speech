# Text-to-Speech Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Python application that converts text to speech using OpenAI's Text-to-Speech API. Designed for handling texts of any size with automatic chunking and seamless audio stitching.

> 📌 **Repository**: [github.com/theosp/open-ai-text-to-speech](https://github.com/theosp/open-ai-text-to-speech)

## Features

- Convert text from files to speech with high-quality results
- Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
- Robust command-line interface with intuitive options
- Smart handling of large files with automatic chunking and stitching
- Cost estimation before processing to avoid surprises
- Comprehensive test suite with 78% code coverage
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

## Testing

The project includes a comprehensive test suite with:

- Unit tests
- Integration tests
- Property-based testing (with Hypothesis)
- Error injection testing
- Code coverage reporting

### Running Tests

Basic test execution:

```bash
# Run all tests
pytest

# Run with test discovery details
pytest -v
```

### Using the Test Runner

The project includes a convenient test runner script:

```bash
# Run all tests
./run_tests.py

# Run tests with coverage report
./run_tests.py --coverage

# Generate HTML coverage report
./run_tests.py --coverage --html

# Run specific test files
./run_tests.py tests/test_advanced.py

# Show detailed error information
./run_tests.py --detailed-errors
```

### Code Coverage

The project uses pytest-cov for code coverage analysis:

```bash
# Generate coverage report
pytest --cov=generator

# Generate HTML coverage report
pytest --cov=generator --cov-report=html
# Then open htmlcov/index.html in your browser
```

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