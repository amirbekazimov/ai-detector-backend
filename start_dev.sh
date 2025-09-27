#!/bin/bash

# Local development server startup script
echo "Starting AI Detector Backend in development mode..."

# Set environment variables for local development
export ENVIRONMENT=development
export DEBUG=true
export SECRET_KEY="ai-detector-super-secret-key-change-in-production-2024"

# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
