"""Site endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.site import Site, SiteCreate, SiteUpdate
from app.services.site_service import SiteService
from app.models.user import User
from app.core.config import settings

router = APIRouter()


@router.post("/sites", response_model=Site)
async def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new site."""
    site_service = SiteService(db)
    
    # Check site limit (max 3 sites per user)
    if site_service.count_user_sites(current_user.id) >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 sites allowed per user"
        )
    
    try:
        site = site_service.create_site(site_data, current_user.id)
        return site
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create site: {str(e)}"
        )


@router.get("/sites", response_model=List[Site])
async def get_user_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all sites for current user."""
    site_service = SiteService(db)
    return site_service.get_user_sites(current_user.id)


@router.get("/sites/{site_id}", response_model=Site)
async def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific site by ID."""
    site_service = SiteService(db)
    site = site_service.get_site(site_id, current_user.id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return site


@router.get("/sites/{site_id}/tracking-code")
async def get_tracking_code(
    site_id: str,
    db: Session = Depends(get_db)
):
    """Get tracking code for a specific site."""
    site_service = SiteService(db)
    
    # Try by numeric ID first, then by site_id string
    site = None
    try:
        numeric_id = int(site_id)
        site = site_service.get_site_by_id(numeric_id)
    except ValueError:
        # If not numeric, try by site_id string
        site = site_service.get_site_by_site_id(site_id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Generate tracking code snippet
    tracking_code = f"""<!-- AI Detector Tracking Code -->
<script src="{settings.API_URL}/api/v1/tracking/{site.site_id}.js"></script>
<!-- End AI Detector -->"""
    
    return {
        "site_id": site.site_id,
        "site_name": site.name,
        "domain": site.domain,
        "tracking_code": tracking_code,
        "script_url": f"{settings.API_URL}/api/v1/tracking/{site.site_id}.js",
        "server_page_url": f"{settings.API_URL}/api/v1/client-page?site_id={site.site_id}",
        "instructions": {
            "step1": "Copy the tracking code above and paste it before the closing </body> tag on your website",
            "step2": "The script will automatically detect AI bots visiting your site",
            "step3": "For testing with ChatGPT, use the server page URL",
            "step4": "View detection results in your dashboard",
            "note": "Server page URL works for AI bots that don't execute JavaScript"
        }
    }


@router.put("/sites/{site_id}", response_model=Site)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update site."""
    site_service = SiteService(db)
    site = site_service.update_site(site_id, site_data, current_user.id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return site


@router.delete("/sites/{site_id}")
async def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete site."""
    site_service = SiteService(db)
    success = site_service.soft_delete_site(site_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return {"message": "Site deleted successfully"}


@router.get("/sites/{site_id}/snippet")
async def get_js_snippet(
    site_id: str,  # Исправлено: str вместо int
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get JavaScript snippet for site."""
    site_service = SiteService(db)
    site = site_service.get_site_by_site_id(site_id)  # Исправлено: используем get_site_by_site_id
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Проверяем что сайт принадлежит текущему пользователю
    if site.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Generate JavaScript snippet
    js_snippet = f"""
<!-- AI Detector Script -->
<script>
(function() {{
    var script = document.createElement('script');
    script.src = '{settings.API_URL}/api/v1/tracking/{site.site_id}.js';
    script.async = true;
    document.head.appendChild(script);
}})();
</script>
<!-- End AI Detector Script -->
""".strip()
    
    return {
        "site_id": site.site_id,
        "domain": site.domain,
        "js_snippet": js_snippet,
        "instructions": "Copy and paste this code before the closing </body> tag on your website."
    }
