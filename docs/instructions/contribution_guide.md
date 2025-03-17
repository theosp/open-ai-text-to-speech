# Contribution Guide

This document provides guidelines for contributing to the Text-to-Speech application. It outlines the process for making changes, running tests, and submitting pull requests.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd text-to-speech
   ```

2. **Set up the Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the Node.js environment for client-side testing:**
   ```bash
   npm install
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env to add your OpenAI API key
   ```

5. **Build and run the Docker container (optional):**
   ```bash
   docker compose up --build -d
   ```

## Development Workflow

1. **Create a new branch for your changes:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following the project's code style.**

3. **Run the linters:**
   ```bash
   # Python
   flake8
   pylint app generator utils tests
   
   # JavaScript
   npm run lint
   ```

4. **Run the tests:**
   ```bash
   # Python tests
   pytest
   
   # JavaScript tests
   npm test
   
   # All tests with coverage
   pytest --cov=app --cov=generator --cov=utils
   npm run test:coverage
   ```

5. **Commit your changes with descriptive commit messages:**
   ```bash
   git add .
   git commit -m "Add feature: Description of your changes"
   ```

6. **Push your branch to the remote repository:**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request on GitHub.**

## Code Style Guidelines

### Python

- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length is 88 characters
- Use docstrings for functions and classes
- Use type hints where appropriate

### JavaScript

- Use ES6 syntax
- Use 2 spaces for indentation
- Use semicolons at the end of statements
- Use camelCase for variables and functions
- Use PascalCase for classes and components

### HTML/CSS

- Use 2 spaces for indentation
- Use lowercase for HTML tags and attributes
- Use kebab-case for CSS classes and IDs

## Testing Requirements

All contributions must include appropriate tests that cover the new functionality or fix. The project has the following testing requirements:

### Python Testing

- All Python code should have unit tests using pytest
- Minimum test coverage: 80%
- Required test categories:
  - Text chunking functionality
  - Cost calculation accuracy
  - OpenAI API integration
  - Audio stitching for long texts

### JavaScript Testing

- All JavaScript code should have unit tests using Jest
- Minimum test coverage: 75%
- Required test categories:
  - Character count functionality
  - Cost preview calculations
  - UI interaction
  - Form submission

### Docker Testing

- All changes to Docker configuration should be tested
- Health check endpoint must be tested
- Mock mode for API calls must be supported

## Pull Request Process

1. **Ensure your code passes all tests and linters.**
2. **Update documentation if necessary.**
3. **Include a clear description of the changes in your pull request.**
4. **Link any related issues in your pull request description.**
5. **Wait for code review and address any feedback.**
6. **Once approved, your changes will be merged into the main branch.**

## Continuous Integration

The project uses GitHub Actions for continuous integration. Every pull request triggers the following checks:

1. **Python tests:** Runs all Python tests with coverage reporting
2. **JavaScript tests:** Runs all JavaScript tests with coverage reporting
3. **Docker build:** Builds and tests the Docker container
4. **Linting:** Runs linters for Python and JavaScript code

## Versioning

The project follows Semantic Versioning (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible feature additions
- **PATCH** version for backward-compatible bug fixes

## Release Process

1. **Update version number in relevant files.**
2. **Update CHANGELOG.md with changes since the last release.**
3. **Create a new release tag on GitHub.**
4. **Build and publish the Docker image.**

## Need Help?

If you have questions or need help with contributing, please:

1. Check the documentation in the `docs` directory
2. Open an issue with the "question" label
3. Reach out to the maintainers 