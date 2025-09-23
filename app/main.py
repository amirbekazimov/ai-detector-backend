"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health, detections, auth
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(detections.router, prefix=f"{settings.API_V1_STR}/detections", tags=["detections"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Detector API",
        "version": settings.VERSION,
        "docs": "/docs"
    }
