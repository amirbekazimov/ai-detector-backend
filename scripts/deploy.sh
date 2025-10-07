#!/bin/bash

echo "🚀 Starting AI Detector Deployment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found! Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install Alembic if not present
if ! command -v alembic &> /dev/null; then
    echo "📦 Installing Alembic..."
    pip install alembic
fi

# Check database connection
echo "🔍 Checking database connection..."
python -c "
from app.core.config import settings
from sqlalchemy import create_engine
try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Show final migration status
echo "📊 Final migration status:"
alembic current

echo "🎉 Deployment completed successfully!"
echo "📝 Next steps:"
echo "   - Start your application server"
echo "   - Check logs for any issues"
echo "   - Verify all endpoints are working"
