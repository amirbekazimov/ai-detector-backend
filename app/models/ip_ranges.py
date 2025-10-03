"""AI Bot IP Ranges model."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func

from app.db.base import Base


class AIBotIPRange(Base):
    """Model for storing AI bot IP ranges and addresses."""

    __tablename__ = "ai_bot_ip_ranges"

    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String, nullable=False, index=True)  # ChatGPT, GPTBot, etc.
    source_type = Column(String, nullable=False, index=True)  # direct_ip, ip_range, cidr
    ip_address = Column(String, nullable=False, index=True)  # Single IP or CIDR
    ip_range_start = Column(String, nullable=True)  # For range entries
    ip_range_end = Column(String, nullable=True)  # For range entries
    source_url = Column(Text, nullable=True)  # URL from which the IP was obtained
    is_active = Column(Boolean, default=True, nullable=False)  # Enable/disable filtering
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class IPRangeUpdateLog(Base):
    """Log of IP range updates."""

    __tablename__ = "ip_range_update_log"

    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String, nullable=False, index=True)
    update_type = Column(String, nullable=False)  # full_update, ip_add, ip_remove
    changes_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # How long the update took
    created_at = Column(DateTime(timezone=True), server_default=func.now())
