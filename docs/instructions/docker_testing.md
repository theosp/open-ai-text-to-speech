# Docker Testing Guide

This document provides guidance on testing the Text-to-Speech application in a Docker environment.

## Docker Setup

The application is containerized using Docker with the following key files:

- `Dockerfile`: Defines the container image
- `docker-compose.yml`: Orchestrates the container setup
- `.env`: Contains environment variables (created from `.env.example`)

## Running the Docker Container

```bash
# Build and start the container
docker compose up --build -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

## Testing the Docker Environment

### Automated Testing in Docker

To run the application tests inside the Docker container:

```bash
# Run Python tests inside the container
docker compose exec text-to-speech pytest

# Run Python tests with coverage
docker compose exec text-to-speech pytest --cov=app --cov=generator --cov=utils

# Run client-side tests inside the container
docker compose exec text-to-speech npm test
```

### Manual Testing

1. Start the Docker container:
   ```bash
   docker compose up --build -d
   ```

2. Access the application in a browser:
   ```
   http://localhost:5001/
   ```

3. Test various features:
   - Text input
   - Voice selection
   - Model selection
   - Text-to-speech generation
   - Cost preview
   - Error handling

### Health Check Testing

Test the health check endpoint to verify the application is running correctly:

```bash
curl http://localhost:5001/health
```

Expected response:
```json
{"status": "ok"}
```

## Required Docker Test Cases

### 1. Container Startup

- Test that the container starts successfully
- Verify logs show proper initialization
- Check that the application is accessible at the expected port

Example test script:
```bash
#!/bin/bash

# Start the container
docker compose up --build -d

# Wait for container to initialize
sleep 5

# Check if the service is running
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)

if [ "$response" -eq 200 ]; then
    echo "Container startup: SUCCESS"
else
    echo "Container startup: FAILED"
    exit 1
fi
```

### 2. Environment Variables

- Test proper loading of environment variables
- Test handling of missing environment variables
- Test default values for optional environment variables

Example test:
```bash
#!/bin/bash

# Test with valid API key
docker compose up --build -d
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)
echo "With API key: $response"
docker compose down

# Test with missing API key
mv .env .env.bak
cp .env.example .env
sed -i '' 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=/' .env
docker compose up --build -d
response=$(curl -s http://localhost:5001/)
if echo "$response" | grep -q "API key not found"; then
    echo "Missing API key handling: SUCCESS"
else
    echo "Missing API key handling: FAILED"
fi
docker compose down
mv .env.bak .env
```

### 3. Volume Mounting

- Test that data is persisted through container restarts
- Verify file permissions are set correctly
- Test access to mounted volumes

Example test:
```bash
#!/bin/bash

# Start container
docker compose up --build -d

# Generate a speech file (using mock mode to avoid API calls)
curl -X POST -F "text=Test text" -F "voice=alloy" -F "model=standard" -F "mock_mode=true" http://localhost:5001/generate -o test_output.mp3

# Verify file was created
if [ -f "test_output.mp3" ]; then
    echo "Volume mounting: SUCCESS"
else
    echo "Volume mounting: FAILED"
fi

# Clean up
docker compose down
rm -f test_output.mp3
```

### 4. Resource Usage

- Test CPU usage during text-to-speech generation
- Test memory usage with large text inputs
- Test disk usage for audio file storage

### 5. Error Handling

- Test application behavior when API key is invalid
- Test recovery from container crashes
- Test logging of errors in Docker logs

Example test:
```bash
#!/bin/bash

# Test with invalid API key
cp .env .env.bak
sed -i '' 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=invalid_key/' .env
docker compose up --build -d

# Test API error handling
response=$(curl -s -X POST -F "text=Test text" -F "voice=alloy" -F "model=standard" http://localhost:5001/generate)
if echo "$response" | grep -q "error"; then
    echo "Error handling: SUCCESS"
else
    echo "Error handling: FAILED"
fi

# Restore original env file
docker compose down
mv .env.bak .env
```

### 6. Network Configuration

- Test that the application is accessible at the configured port
- Test port conflicts are handled appropriately
- Test connections to external services (OpenAI API)

## Integration Testing with Docker

To test the full end-to-end functionality in the Docker environment:

1. Create a test script that exercises the full application flow
2. Run the script against the containerized application
3. Verify the results match expected outcomes

Example integration test script:
```bash
#!/bin/bash

# Start the container
docker compose up --build -d

# Wait for the application to initialize
sleep 5

# Test the full flow
echo "Testing full application flow..."

# 1. Check health endpoint
health_response=$(curl -s http://localhost:5001/health)
if echo "$health_response" | grep -q "ok"; then
    echo "Health check: PASSED"
else
    echo "Health check: FAILED"
    exit 1
fi

# 2. Test cost preview (using fetch in browser would be more realistic)
cost_response=$(curl -s -X POST \
    -F "text=This is a test of the text to speech system" \
    -F "model=standard" \
    http://localhost:5001/calculate_cost)
if echo "$cost_response" | grep -q "cost"; then
    echo "Cost preview: PASSED"
else
    echo "Cost preview: FAILED"
    exit 1
fi

# 3. Test speech generation with mock mode
gen_response=$(curl -s -X POST \
    -F "text=This is a test of the text to speech system" \
    -F "voice=alloy" \
    -F "model=standard" \
    -F "mock_mode=true" \
    http://localhost:5001/generate -o test_output.mp3)

if [ -f "test_output.mp3" ] && [ -s "test_output.mp3" ]; then
    echo "Speech generation: PASSED"
else
    echo "Speech generation: FAILED"
    exit 1
fi

# Clean up
rm -f test_output.mp3
docker compose down

echo "All tests completed successfully!"
```

## Best Practices for Docker Testing

1. **Isolation**: Each test should run in an isolated environment
2. **Cleanup**: Always clean up containers and volumes after testing
3. **Automation**: Automate the testing process with scripts
4. **CI Integration**: Integrate Docker tests into CI/CD pipeline
5. **Mock External Services**: Use mock mode to avoid real API calls
6. **Resource Monitoring**: Monitor resource usage during testing
7. **Security Testing**: Verify that the container is secure
8. **Version Consistency**: Test with the same Docker version used in production
9. **Network Validation**: Test network configurations and connectivity
10. **Logging**: Validate proper logging in the Docker environment 