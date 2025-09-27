"""Site model."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Site(Base):
    """Site model."""

    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, default="")  # Site name (default empty for backward compatibility)
    domain = Column(String, nullable=False)
    site_id = Column(String, unique=True, nullable=False, index=True)  # Unique identifier for JS snippet
    is_active = Column(Boolean, default=True)  # For soft delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete timestamp
