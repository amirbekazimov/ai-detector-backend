# AI Detector Backend

Professional FastAPI project for AI-generated content detection.

## Project Structure

```
ai-detector-backend/
├── app/                    # Main application
│   ├── api/               # API endpoints
│   │   ├── v1/            # API version v1
│   │   │   └── endpoints/ # Specific endpoints
│   │   └── deps.py        # API dependencies
│   ├── core/              # Core configuration
│   ├── db/                # Database
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utilities
│   └── main.py           # FastAPI entry point
├── scripts/              # Management scripts
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

## Quick Start

### 1. Install PostgreSQL

**macOS (with Homebrew):**

```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install PostgreSQL from the official website.

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_detector;
CREATE USER ai_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ai_detector TO ai_user;
\q
```

### 3. Install Project

```bash
cd ai-detector-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Setup Environment

```bash
# Create .env file with proper keys
./scripts/create_env.sh
```

### 5. Run

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use ready script
./scripts/start_dev.sh
```

## API Documentation

After starting the server, documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Main Endpoints

- `GET /` - Root page
- `GET /api/v1/health` - Health check
- `POST /api/v1/detections/detect` - AI content detection
- `GET /api/v1/detections` - Get all detections
- `GET /api/v1/detections/{id}` - Get specific detection

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Testing

```bash
pytest
pytest -v  # Verbose output
pytest --cov=app  # With code coverage
```

### Linting

```bash
# Install additional tools
pip install black isort flake8

# Format code
black app/
isort app/

# Check style
flake8 app/
```

## Technologies

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Alembic** - Migrations (optional)
- **pytest** - Testing

## Configuration

Main environment variables in `.env`:

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=ai-detector-super-secret-key-change-in-production-2024

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_detector
POSTGRES_PORT=5432

# CORS Configuration (for frontend)
BACKEND_CORS_ORIGINS_STR=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080
```

## Production Deployment

1. Set environment variables for production
2. Use PostgreSQL in production
3. Use reverse proxy (nginx)
4. Setup monitoring and logging
5. Consider adding Redis for caching
6. Use Docker for containerization

## License

MIT License
