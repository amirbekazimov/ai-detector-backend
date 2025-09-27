#!/bin/bash

echo "🔧 Setting up PostgreSQL for AI Detector..."

# Create database
echo "📦 Creating database 'ai_detector'..."
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE ai_detector;" 2>/dev/null || echo "Database might already exist"

# Set password for postgres user
echo "🔑 Setting password for postgres user..."
psql -h localhost -U postgres -d postgres -c "ALTER USER postgres PASSWORD 'password';" 2>/dev/null || echo "Password might already be set"

echo "✅ PostgreSQL setup complete!"
echo ""
echo "📋 Connection details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   User: postgres"
echo "   Password: password"
echo "   Database: ai_detector"
echo ""
echo "🚀 Now you can start the backend:"
echo "   ./start_dev.sh"
