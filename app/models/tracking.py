"""Tracking event model."""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class TrackingEvent(Base):
    """Tracking event model."""

    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, nullable=False, index=True)  # site_id from Site model
    event_type = Column(String, nullable=False, index=True)  # page_view, click, etc.
    url = Column(Text, nullable=False)
    path = Column(String, nullable=True)
    title = Column(String, nullable=True)
    referrer = Column(Text, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)  # IP address of visitor
    screen_resolution = Column(String, nullable=True)
    viewport_size = Column(String, nullable=True)
    language = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    event_data = Column(JSON, nullable=True)  # Additional event-specific data
    
    # AI Bot Detection
    is_ai_bot = Column(String, nullable=True)  # Bot name if detected, null if not
    bot_name = Column(String, nullable=True)  # Name of the AI bot (GPTBot, Perplexity, etc.)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
