#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting CI/CD pipeline for Text-to-Speech application...${NC}"

# Step 1: Build the Docker image
echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
docker compose build

# Step 2: Start the container
echo -e "${YELLOW}Step 2: Starting Docker container...${NC}"
docker compose up -d

# Step 3: Wait for the container to be ready
echo -e "${YELLOW}Step 3: Waiting for container to be ready...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Attempt $(($RETRY_COUNT+1))/$MAX_RETRIES..."
    if curl -s http://localhost:5001/api/health > /dev/null; then
        echo -e "${GREEN}Container is ready!${NC}"
        break
    fi
    
    RETRY_COUNT=$(($RETRY_COUNT+1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${RED}Container failed to start properly after $MAX_RETRIES attempts.${NC}"
        docker compose logs
        docker compose down
        exit 1
    fi
    
    echo "Waiting 2 seconds..."
    sleep 2
done

# Step 4: Run the tests
echo -e "${YELLOW}Step 4: Running tests...${NC}"
python run_docker_tests.py
TEST_RESULT=$?

# Step 5: Clean up
echo -e "${YELLOW}Step 5: Cleaning up...${NC}"
docker compose down

# Step 6: Report results
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}CI/CD pipeline completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}CI/CD pipeline failed. See test output above for details.${NC}"
    exit 1
fi 