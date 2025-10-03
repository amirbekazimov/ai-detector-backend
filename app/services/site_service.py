"""Site service."""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.site import Site as SiteModel
from app.schemas.site import SiteCreate, SiteUpdate, Site as SiteSchema


class SiteService:
    """Service for site operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_site(self, site_data: SiteCreate, user_id: int) -> SiteSchema:
        """Create a new site."""
        # Generate unique site_id for JS snippet
        site_id = f"site_{uuid.uuid4().hex[:12]}"
        
        db_site = SiteModel(
            user_id=user_id,
            name=site_data.name,
            domain=site_data.domain,
            site_id=site_id
        )
        
        self.db.add(db_site)
        self.db.commit()
        self.db.refresh(db_site)
        
        return SiteSchema.from_orm(db_site)
    
    def get_user_sites(self, user_id: int, include_deleted: bool = False) -> List[SiteSchema]:
        """Get all sites for a user with statistics."""
        from app.services.tracking_service import TrackingEventService
        
        query = self.db.query(SiteModel).filter(SiteModel.user_id == user_id)
        
        if not include_deleted:
            query = query.filter(SiteModel.is_active == True)
        
        sites = query.all()
        tracking_service = TrackingEventService(self.db)
        
        # Add statistics to each site
        sites_with_stats = []
        for site in sites:
            site_dict = SiteSchema.from_orm(site).dict()
            
            # Get statistics for the last 30 days
            stats = tracking_service.get_site_stats(site.site_id, 30)
            
            site_dict.update({
                'total_events': stats['total_events'],
                'ai_bot_events': stats['ai_bot_events'],
                'human_events': stats['human_events'],
                'ai_bot_percentage': stats['ai_bot_percentage']
            })
            
            sites_with_stats.append(SiteSchema(**site_dict))
        
        return sites_with_stats
    
    def get_site(self, site_id: int, user_id: int) -> Optional[SiteSchema]:
        """Get site by ID for specific user."""
        site = self.db.query(SiteModel).filter(
            and_(SiteModel.id == site_id, SiteModel.user_id == user_id)
        ).first()
        
        if site:
            return SiteSchema.from_orm(site)
        return None
    
    def get_site_by_id(self, site_id: int) -> Optional[SiteSchema]:
        """Get site by ID (public for tracking endpoints)."""
        site = self.db.query(SiteModel).filter(SiteModel.id == site_id).first()
        
        if site:
            return SiteSchema.from_orm(site)
        return None
    
    def update_site(self, site_id: int, site_data: SiteUpdate, user_id: int) -> Optional[SiteSchema]:
        """Update site."""
        site = self.db.query(SiteModel).filter(
            and_(SiteModel.id == site_id, SiteModel.user_id == user_id, SiteModel.is_active == True)
        ).first()
        
        if not site:
            return None
        
        if site_data.domain is not None:
            site.domain = site_data.domain
        
        if site_data.name is not None:
            site.name = site_data.name
        
        self.db.commit()
        self.db.refresh(site)
        
        return SiteSchema.from_orm(site)
    
    def soft_delete_site(self, site_id: int, user_id: int) -> bool:
        """Soft delete site (mark as inactive and set deleted_at)."""
        site = self.db.query(SiteModel).filter(
            and_(SiteModel.id == site_id, SiteModel.user_id == user_id, SiteModel.is_active == True)
        ).first()
        
        if not site:
            return False
        
        site.is_active = False
        site.deleted_at = func.now()
        
        self.db.commit()
        return True
    
    def count_user_sites(self, user_id: int) -> int:
        """Count active sites for user."""
        return self.db.query(SiteModel).filter(
            and_(SiteModel.user_id == user_id, SiteModel.is_active == True)
        ).count()
    
    def get_site_by_site_id(self, site_id: str) -> Optional[SiteSchema]:
        """Get site by site_id (for JS snippet)."""
        site = self.db.query(SiteModel).filter(
            and_(SiteModel.site_id == site_id, SiteModel.is_active == True)
        ).first()
        
        if site:
            return SiteSchema.from_orm(site)
        return None
