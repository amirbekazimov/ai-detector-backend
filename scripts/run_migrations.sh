#!/bin/bash

echo "🚀 Running Alembic Migrations..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    echo "Create it with: python3 -m venv venv"
    exit 1
fi

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "❌ Alembic not found! Installing..."
    pip install alembic
fi

# Show current migration status
echo "📊 Current migration status:"
alembic current

# Apply all pending migrations
echo "🔄 Applying migrations..."
alembic upgrade head

echo "✅ Migrations completed successfully!"
echo "📊 Final migration status:"
alembic current
