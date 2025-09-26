"""Dashboard endpoints for tracking statistics."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.services.tracking_service import TrackingEventService
from app.services.site_service import SiteService
from app.models.user import User

router = APIRouter()


@router.get("/stats/{site_id}")
async def get_site_stats(
    site_id: str,
    days: int = Query(default=7, ge=1, le=30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific site."""
    # Verify user owns the site
    site_service = SiteService(db)
    site = site_service.get_site_by_site_id(site_id)
    
    if not site or site.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    tracking_service = TrackingEventService(db)
    stats = tracking_service.get_site_stats(site_id, days)
    
    return {
        "site_id": site_id,
        "domain": site.domain,
        "period_days": days,
        "total_events": stats["total_events"],
        "ai_bot_events": stats["ai_bot_events"],
        "human_events": stats["human_events"],
        "ai_bot_percentage": stats["ai_bot_percentage"],
        "events_by_type": stats["events_by_type"],
        "unique_visitors": stats["unique_visitors"]
    }


@router.get("/visits/{site_id}")
async def get_site_visits(
    site_id: str,
    days: int = Query(default=7, ge=1, le=30, description="Number of days to analyze"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of visits to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent visits for a specific site."""
    # Verify user owns the site
    site_service = SiteService(db)
    site = site_service.get_site_by_site_id(site_id)
    
    if not site or site.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    tracking_service = TrackingEventService(db)
    
    # Get visits (page_view events)
    visits = tracking_service.get_site_events_by_type(site_id, "page_view", limit)
    
    # Format visits for dashboard
    formatted_visits = []
    for visit in visits:
        formatted_visits.append({
            "id": visit.id,
            "timestamp": visit.timestamp.isoformat(),
            "bot_name": visit.bot_name if visit.is_ai_bot else "unknown",
            "user_agent": visit.user_agent,
            "ip_address": visit.ip_address,
            "path": visit.path,
            "url": visit.url,
            "is_ai_bot": visit.is_ai_bot is not None,
            "referrer": visit.referrer
        })
    
    return {
        "site_id": site_id,
        "domain": site.domain,
        "visits": formatted_visits,
        "total_count": len(formatted_visits),
        "limit": limit,
        "offset": offset
    }


@router.get("/daily-stats/{site_id}")
async def get_daily_stats(
    site_id: str,
    days: int = Query(default=7, ge=1, le=30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily statistics for a specific site."""
    # Verify user owns the site
    site_service = SiteService(db)
    site = site_service.get_site_by_site_id(site_id)
    
    if not site or site.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    tracking_service = TrackingEventService(db)
    
    # Get daily stats
    daily_stats = tracking_service.get_daily_stats(site_id, days)
    
    return {
        "site_id": site_id,
        "domain": site.domain,
        "period_days": days,
        "daily_stats": daily_stats
    }


@router.get("/sites")
async def get_user_sites_for_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's sites with basic stats for dashboard."""
    site_service = SiteService(db)
    tracking_service = TrackingEventService(db)
    
    sites = site_service.get_user_sites(current_user.id)
    
    sites_with_stats = []
    for site in sites:
        stats = tracking_service.get_site_stats(site.site_id, 7)  # Last 7 days
        sites_with_stats.append({
            "id": site.id,
            "site_id": site.site_id,
            "domain": site.domain,
            "total_events": stats["total_events"],
            "ai_bot_events": stats["ai_bot_events"],
            "human_events": stats["human_events"],
            "ai_bot_percentage": stats["ai_bot_percentage"],
            "created_at": site.created_at.isoformat()
        })
    
    return {
        "sites": sites_with_stats,
        "total_sites": len(sites_with_stats)
    }
