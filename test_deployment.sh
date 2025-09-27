#!/bin/bash

# Test script to verify deployment compatibility
echo "🧪 Testing AI Detector Backend for deployment compatibility..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test Python version compatibility
test_python_version() {
    echo -e "\n${YELLOW}Testing Python version compatibility...${NC}"
    python_version=$(python --version 2>&1)
    echo "Python version: $python_version"
    
    # Check if it's Python 3.13
    if [[ $python_version == *"3.13"* ]]; then
        echo -e "${RED}⚠️  WARNING: Python 3.13 detected. This may cause compatibility issues.${NC}"
        echo -e "${YELLOW}Consider using Python 3.11 or 3.12 for better compatibility.${NC}"
        echo -e "${YELLOW}Alternative: Use requirements-python311.txt for Python 3.11${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Python version looks good${NC}"
        return 0
    fi
}

# Function to test imports
test_imports() {
    echo -e "\n${YELLOW}Testing imports...${NC}"
    
    # Test basic imports
    python -c "
try:
    import fastapi
    print('✅ FastAPI imported successfully')
except Exception as e:
    print(f'❌ FastAPI import failed: {e}')
    exit(1)

try:
    import pydantic
    print('✅ Pydantic imported successfully')
except Exception as e:
    print(f'❌ Pydantic import failed: {e}')
    exit(1)

try:
    import jwt
    print('✅ PyJWT imported successfully')
except Exception as e:
    print(f'❌ PyJWT import failed: {e}')
    exit(1)

try:
    from argon2 import PasswordHasher
    print('✅ Argon2 imported successfully')
except Exception as e:
    print(f'❌ Argon2 import failed: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All imports successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Import test failed${NC}"
        return 1
    fi
}

# Function to test app import
test_app_import() {
    echo -e "\n${YELLOW}Testing app import...${NC}"
    
    # Set environment for SQLite
    export ENVIRONMENT=development
    
    python -c "
import os
os.environ['ENVIRONMENT'] = 'development'

try:
    from app.main import app
    print('✅ App imported successfully')
except Exception as e:
    print(f'❌ App import failed: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ App import successful${NC}"
        return 0
    else
        echo -e "${RED}❌ App import failed${NC}"
        return 1
    fi
}

# Function to test server startup
test_server_startup() {
    echo -e "\n${YELLOW}Testing server startup...${NC}"
    
    # Kill any existing processes on port 8001
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    
    # Set environment for SQLite
    export ENVIRONMENT=development
    
    # Start server in background
    timeout 10s uvicorn app.main:app --host 0.0.0.0 --port 8001 --log-level error &
    server_pid=$!
    
    # Wait a bit for server to start
    sleep 3
    
    # Test if server is running
    if ps -p $server_pid > /dev/null; then
        echo -e "${GREEN}✅ Server started successfully${NC}"
        
        # Test health endpoint
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/v1/health 2>/dev/null || echo "000")
        if [ "$response" = "200" ]; then
            echo -e "${GREEN}✅ Health endpoint responding${NC}"
        else
            echo -e "${YELLOW}⚠️  Health endpoint not responding (this might be normal)${NC}"
        fi
        
        # Kill server
        kill $server_pid 2>/dev/null || true
        return 0
    else
        echo -e "${RED}❌ Server failed to start${NC}"
        return 1
    fi
}

# Main test function
run_tests() {
    echo "Starting compatibility tests..."
    
    local failed_tests=0
    
    # Run all tests
    test_python_version || ((failed_tests++))
    test_imports || ((failed_tests++))
    test_app_import || ((failed_tests++))
    test_server_startup || ((failed_tests++))
    
    echo -e "\n${YELLOW}=== TEST SUMMARY ===${NC}"
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! Ready for deployment.${NC}"
        return 0
    else
        echo -e "${RED}❌ $failed_tests test(s) failed. Fix issues before deployment.${NC}"
        return 1
    fi
}

# Run tests
run_tests
