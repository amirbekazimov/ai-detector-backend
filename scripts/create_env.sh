#!/bin/bash

echo "Creating .env file with proper configuration..."

cat > .env << 'EOF'
# AI Detector Backend - Environment Variables

ENVIRONMENT=development
DEBUG=true

SECRET_KEY=ai-detector-super-secret-key-change-in-production-2024

POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_detector
POSTGRES_PORT=5432

BACKEND_CORS_ORIGINS_STR=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080
EOF

echo ".env file created successfully!"
echo ""
echo "Configuration details:"
echo "  - Environment: development"
echo "  - Debug mode: enabled"
echo "  - Database: PostgreSQL on localhost:5432"
echo "  - Database name: ai_detector"
echo "  - CORS: enabled for localhost frontends"
echo ""
echo "Security note:"
echo "  - Change SECRET_KEY in production!"
echo "  - Update database credentials as needed"
echo ""
echo "Ready to start the server!"
