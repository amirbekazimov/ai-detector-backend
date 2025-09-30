#!/bin/bash

# Safe deployment script for Render.com
# This script ensures backward compatibility during deployment

echo "🚀 Starting safe deployment to Render..."

# Set environment variables for production
export ENVIRONMENT=production
export DEBUG=false

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔄 Running database migration..."
python migrate_add_site_name.py

echo "🏗️ Starting application..."
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

