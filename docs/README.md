# Text-to-Speech Application Documentation

This directory contains comprehensive documentation for the Text-to-Speech application, including project structure, testing guides, bug fixes, and best practices.

## Documentation Structure

### Instructions for Developers

The `instructions/` directory contains guidance for developers working on the project:

- [Project Overview](instructions/project_overview.md) - High-level overview of the application architecture and functionality
- [Testing Guide](instructions/testing_guide.md) - Comprehensive testing strategy and requirements
- [Client-Side Testing](instructions/client_side_testing.md) - Specific guidance for JavaScript tests
- [Server-Side Testing](instructions/server_side_testing.md) - Specific guidance for Python tests
- [Docker Testing](instructions/docker_testing.md) - How to test Docker configuration
- [Advanced Test Scenarios](instructions/advanced_test_scenarios.md) - Complex testing scenarios
- [Bug Prevention](instructions/bug_prevention.md) - Strategies to prevent common bugs
- [Contribution Guide](instructions/contribution_guide.md) - Guidelines for contributing to the project

### Bug Fix Documentation

The `bug_fixes/` directory documents significant bugs that have been addressed:

- [Text Display Fix](bug_fixes/text_display_fix.md) - Resolution for the issue where input text wasn't displayed on the result page

## Development Environment

The application is configured to run in a Docker container, exposing port 5001 for web access. Developers can run tests both inside and outside the container.

### Key Configuration Files

- `.cursorrules` - Contains project-specific linting rules and testing requirements
- `docker-compose.yml` - Defines the Docker container configuration
- `Dockerfile` - Instructions for building the application container

## Testing Requirements

All changes to the codebase must be tested according to the guidelines in the testing documentation. The project requires:

1. **Python Tests**: Minimum 80% coverage for server-side code
2. **JavaScript Tests**: Minimum 75% coverage for client-side code
3. **Regression Tests**: New fixes must include tests that would have caught the original issue
4. **Docker Tests**: Container must be tested before deployment

## Getting Started

New developers should:

1. Read the [Project Overview](instructions/project_overview.md) first
2. Review the [Testing Guide](instructions/testing_guide.md)
3. Set up the development environment following the main project README
4. Run all tests before making changes: `pytest tests/` and `npm test`

## Updating Documentation

When making significant changes to the codebase, please update the relevant documentation. For bug fixes, create a new file in the `bug_fixes/` directory following the template in existing files. 