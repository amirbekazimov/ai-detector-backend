"""Site endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.site import Site, SiteCreate, SiteUpdate
from app.services.site_service import SiteService
from app.models.user import User

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
    """Get specific site by ID."""
    site_service = SiteService(db)
    site = site_service.get_site(site_id, current_user.id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return site


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
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get JavaScript snippet for site."""
    site_service = SiteService(db)
    site = site_service.get_site(site_id, current_user.id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Generate JavaScript snippet
    js_snippet = f"""
<!-- AI Detector Script -->
<script>
(function() {{
    var script = document.createElement('script');
    script.src = 'http://localhost:8000/api/v1/tracking/{site.site_id}.js';
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
