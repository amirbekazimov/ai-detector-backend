"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, detections, auth, sites, tracking, dashboard, ip_ranges, public, server_code, server_detection
from app.core.config import settings
from app.services.scheduler_service import scheduler_service

# for new db tables auto create tables if they don't exist (will work on Supabase)
from app.db.session import engine
from app.db.base import Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# auto create tables if they don't exist (will work on Supabase)
Base.metadata.create_all(bind=engine)

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
app.include_router(ip_ranges.router, prefix=f"{settings.API_V1_STR}", tags=["ip-ranges"])
app.include_router(public.router, prefix=f"{settings.API_V1_STR}", tags=["public"])
app.include_router(server_code.router, prefix=f"{settings.API_V1_STR}", tags=["server-code"])
app.include_router(server_detection.router, prefix=f"{settings.API_V1_STR}", tags=["server-detection"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting AI Detector API...")
    
    # Start scheduler service
    scheduler_service.start_scheduler()
    print("✅ Scheduler service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("🛑 Shutting down AI Detector API...")
    
    # Stop scheduler service
    scheduler_service.stop_scheduler()
    print("✅ Scheduler service stopped")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Detector API",
        "version": settings.VERSION,
        "docs": "/docs",
                "features": {
                    "ai_bot_detection": "User-Agent + IP address based detection",
                    "ip_range_updates": "Daily updates from GitHub + crawlers-info.de",
                    "real_time_tracking": "JavaScript-based tracking snippet",
                    "site_management": "Create sites and get tracking codes",
                    "dashboard": "View AI bot detection statistics",
                    "scheduler": "Automated daily IP updates at 05:00 and 06:00"
                }
    }
