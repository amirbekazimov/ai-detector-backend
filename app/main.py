"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, detections, auth, sites, tracking, dashboard
from app.core.config import settings

# for new db tables auto create tables if they don't exist (will work on Supabase)
from app.db.session import engine
from app.db.base import Base

# migration for new db tables
def run_migrations():
    """Run database migrations."""
    try:
        with engine.connect() as conn:
            # Check if name column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sites' AND column_name='name'
            """))
            
            if not result.fetchone():
                print("🔄 Adding 'name' column to sites table...")
                conn.execute(text("""
                    ALTER TABLE sites 
                    ADD COLUMN name VARCHAR NOT NULL DEFAULT ''
                """))
                conn.commit()
                
                # Update existing sites to use domain as name
                result = conn.execute(text("""
                    UPDATE sites 
                    SET name = domain 
                    WHERE name = '' OR name IS NULL
                """))
                conn.commit()
                print(f"✅ Migration completed! Updated {result.rowcount} sites")
            else:
                print("✅ Column 'name' already exists. Migration not needed.")
                
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
        # Don't fail startup if migration fails

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# auto create tables if they don't exist (will work on Supabase)
Base.metadata.create_all(bind=engine)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(detections.router, prefix=f"{settings.API_V1_STR}/detections", tags=["detections"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(sites.router, prefix=settings.API_V1_STR, tags=["sites"])
app.include_router(tracking.router, prefix=f"{settings.API_V1_STR}/tracking", tags=["tracking"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Detector API",
        "version": settings.VERSION,
        "docs": "/docs"
    }
