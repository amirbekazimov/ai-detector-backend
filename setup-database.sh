#!/bin/bash

echo "🔧 Setting up PostgreSQL database for AI Detector..."

# Create database
echo "📦 Creating database 'ai_detect_db'..."
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE ai_detect_db;" 2>/dev/null || echo "Database might already exist"

echo "✅ Database setup complete!"
echo ""
echo "📋 Connection details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   User: postgres"
echo "   Password: root123"
echo "   Database: ai_detect_db"
echo ""
echo "🚀 Now run migration and start backend:"
echo "   python migrate_add_site_name.py"
echo "   ./start_dev.sh"
