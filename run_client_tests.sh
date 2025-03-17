#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting client-side tests for Text-to-Speech application...${NC}"

# Step 1: Check if Docker container is running
echo -e "${YELLOW}Step 1: Checking if Docker container is running...${NC}"
if ! curl -s http://localhost:5001/api/health > /dev/null; then
    echo -e "${YELLOW}Docker container not running. Starting it...${NC}"
    docker compose up -d
    
    # Wait for container to be ready
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
else
    echo -e "${GREEN}Docker container is already running.${NC}"
fi

# Step 2: Install Node.js dependencies
echo -e "${YELLOW}Step 2: Installing Node.js dependencies...${NC}"
npm install

# Step 3: Run the Jest tests
echo -e "${YELLOW}Step 3: Running client-side tests...${NC}"
npm test

# Step 4: Run coverage tests
echo -e "${YELLOW}Step 4: Running client-side tests with coverage...${NC}"
npm run test:coverage

# Step 5: Report results
echo -e "${GREEN}Client-side tests completed!${NC}"
echo -e "${YELLOW}Coverage report is available in client-tests/coverage directory.${NC}" 