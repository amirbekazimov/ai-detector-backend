#!/bin/bash

echo "Starting AI Detector Backend..."

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Virtual environment not found!"
    echo "Create it with: python3 -m venv venv"
    exit 1
fi

echo "Checking dependencies..."
pip install -r requirements.txt

echo "Creating database tables..."
python -c "
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.models.user import User, Detection
from app.models.site import Site
from app.models.tracking import TrackingEvent

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully!')
"

echo "Starting FastAPI server..."
echo "API docs available at: http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
