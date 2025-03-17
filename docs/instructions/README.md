# Text-to-Speech Application Documentation

Welcome to the Text-to-Speech application documentation. This directory contains comprehensive guides for understanding, developing, and testing the application.

## Table of Contents

### Overview
- [Project Overview](./project_overview.md) - High-level overview of the project structure and functionality
- [PDF Support](./pdf_support.md) - Documentation for the PDF upload and text extraction feature

### Development Guides
- [Contribution Guide](./contribution_guide.md) - Guidelines for contributing to the project

### Testing Guides
- [Testing Guide](./testing_guide.md) - General testing requirements and strategies
- [Server-Side Testing](./server_side_testing.md) - Python and Flask testing guide
- [Client-Side Testing](./client_side_testing.md) - JavaScript testing with Jest and Puppeteer
- [Docker Testing](./docker_testing.md) - Testing in Docker environment
- [Advanced Test Scenarios](./advanced_test_scenarios.md) - Detailed test cases for complex functionality

## Quick Start

To get started with the project:

1. Review the [Project Overview](./project_overview.md) to understand the application structure
2. Set up your development environment following the [Contribution Guide](./contribution_guide.md)
3. Understand the testing requirements in the [Testing Guide](./testing_guide.md)
4. Run the appropriate tests based on the area you're working on

## Testing Requirements

The project requires comprehensive testing across multiple layers:

1. **Unit Tests** - Individual functions and components
2. **Integration Tests** - Interaction between components
3. **End-to-End Tests** - Complete user flows
4. **Docker Tests** - Functionality in containerized environment

Key test scenarios include:

- Text input handling and character counting
- Cost calculation accuracy
- Text-to-speech conversion with OpenAI API
- Audio stitching for long texts
- User interface interaction
- Error handling

## Development Workflow

1. Fork and clone the repository
2. Create a feature branch
3. Make your changes
4. Add appropriate tests
5. Run all tests to ensure nothing breaks
6. Submit a pull request

See the [Contribution Guide](./contribution_guide.md) for detailed instructions.

## Configuration

The project uses a `.cursorrules` file to define linting, formatting, and testing requirements. Ensure your development environment respects these settings.

## Need Help?

If you have questions or need help with the application, please refer to the appropriate guide or reach out to the project maintainers. 