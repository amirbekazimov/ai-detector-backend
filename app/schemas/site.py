"""Site schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SiteBase(BaseModel):
    """Base site schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Site name")
    domain: str = Field(..., min_length=3, max_length=255, description="Domain name (root or subdomain)")


class SiteCreate(SiteBase):
    """Site creation schema."""
    pass


class SiteUpdate(BaseModel):
    """Site update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    domain: Optional[str] = Field(None, min_length=3, max_length=255)


class SiteInDBBase(SiteBase):
    """Site in database base schema."""
    id: int
    user_id: int
    site_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Site(SiteInDBBase):
    """Site schema for API responses."""
    total_events: Optional[int] = 0
    ai_bot_events: Optional[int] = 0
    human_events: Optional[int] = 0
    ai_bot_percentage: Optional[float] = 0.0


class SiteInDB(SiteInDBBase):
    """Site schema for database."""
    pass
