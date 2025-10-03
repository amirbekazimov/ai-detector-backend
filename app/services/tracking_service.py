"""Tracking event service."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta

from app.models.tracking import TrackingEvent
from app.models.site import Site
from app.services.ai_detection_service import AIBotDetectionService


class TrackingEventService:
    """Service for tracking event operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tracking_event(self, event_data: Dict[str, Any], ip_address: str = None) -> Optional[TrackingEvent]:
        """Create a new tracking event - only for AI bots."""
        user_agent = event_data.get('user_agent')
        
        # Detect AI bot using comprehensive method (User-Agent + IP)
        bot_category, bot_name, detection_method = AIBotDetectionService.detect_ai_bot_comprehensive(
            user_agent, ip_address, self.db
        )
        
        # TEST MODE DISABLED: Only real AI bots are tracked
        # Uncomment the block below to enable test mode
        # if not bot_category:
        #     bot_category = "Test Bot"
        #     bot_name = "TestBot"
        #     print(f"TEST MODE: Treating regular browser as AI bot - User-Agent: {user_agent}")
        
        # Only save events from AI bots (or test mode)
        if not bot_category:
            return None
        
        db_event = TrackingEvent(
            site_id=event_data.get('site_id'),
            event_type=event_data.get('event_type'),
            url=event_data.get('url'),
            path=event_data.get('path'),
            title=event_data.get('title'),
            referrer=event_data.get('referrer'),
            user_agent=user_agent,
            ip_address=ip_address,
            screen_resolution=event_data.get('screen_resolution'),
            viewport_size=event_data.get('viewport_size'),
            language=event_data.get('language'),
            timezone=event_data.get('timezone'),
            event_data=event_data.get('data', {}),
            is_ai_bot=bot_category,
            bot_name=bot_name,
            detection_method=detection_method,
            timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat()))
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        
        return db_event
    
    def create_batch_tracking_events(self, events_data: List[Dict[str, Any]], ip_address: str = None) -> List[TrackingEvent]:
        """Create multiple tracking events from batch data - only for AI bots."""
        events = []
        
        for event_data in events_data:
            event = self.create_tracking_event(event_data, ip_address)
            if event:
                events.append(event)
        
        return events
    
    def get_site_events(self, site_id: str, limit: int = 100, bot_type: str = None) -> List[TrackingEvent]:
        """Get events for a specific site - only AI bots."""
        query = self.db.query(TrackingEvent).filter(TrackingEvent.site_id == site_id)
        
        if bot_type:
            query = query.filter(TrackingEvent.is_ai_bot == bot_type)
            
        return query.order_by(desc(TrackingEvent.timestamp)).limit(limit).all()
    
    def get_site_events_by_type(self, site_id: str, event_type: str, limit: int = 100, bot_type: str = None) -> List[TrackingEvent]:
        """Get events of specific type for a site - only AI bots."""
        query = self.db.query(TrackingEvent).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.event_type == event_type)
        )
        
        if bot_type:
            query = query.filter(TrackingEvent.is_ai_bot == bot_type)

            
        return query.order_by(desc(TrackingEvent.timestamp)).limit(limit).all()
    
    def get_site_stats(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """Get statistics for a site - only AI bots."""
        since_date = datetime.now() - timedelta(days=days)
        
        # All events are AI bot events now
        total_events = self.db.query(TrackingEvent).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).count()
        
        # Events by type
        events_by_type = self.db.query(
            TrackingEvent.event_type,
            func.count(TrackingEvent.id).label('count')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(TrackingEvent.event_type).all()
        
        # Bot types distribution
        bot_types = self.db.query(
            TrackingEvent.is_ai_bot,
            func.count(TrackingEvent.id).label('count')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(TrackingEvent.is_ai_bot).all()
        
        # Unique bot visitors (by user_agent - simplified)
        unique_bots = self.db.query(func.count(func.distinct(TrackingEvent.user_agent))).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).scalar()
        
        return {
            'total_events': total_events,
            'ai_bot_events': total_events,  # All events are AI bot events
            'human_events': 0,  # No human events stored
            'ai_bot_percentage': 100.0,  # All events are AI bots
            'events_by_type': {event_type: count for event_type, count in events_by_type},
            'bot_types': {bot_type: count for bot_type, count in bot_types},
            'unique_visitors': unique_bots,
            'period_days': days
        }
    
    def count_site_events(self, site_id: str) -> int:
        """Count total events for a site."""
        return self.db.query(TrackingEvent).filter(TrackingEvent.site_id == site_id).count()
    
    def get_daily_stats(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """Get daily statistics for a site - only AI bots."""
        since_date = datetime.now() - timedelta(days=days)
        
        # Daily AI bot events
        daily_ai_bot_events = self.db.query(
            func.date(TrackingEvent.timestamp).label('date'),
            func.count(TrackingEvent.id).label('ai_bot_events')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(func.date(TrackingEvent.timestamp)).all()
        
        # Convert to list of dictionaries
        daily_stats = []
        for date, ai_bot_events in daily_ai_bot_events:
            daily_stats.append({
                'date': date.isoformat(),
                'ai_bot_events': ai_bot_events,
                'total_events': ai_bot_events,  # All events are AI bot events
                'ai_bot_percentage': 100.0
            })
        
        return daily_stats
    
    def get_bot_types_stats(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """Get bot types statistics for a site."""
        since_date = datetime.now() - timedelta(days=days)
        
        # Bot types distribution
        bot_types = self.db.query(
            TrackingEvent.is_ai_bot,
            func.count(TrackingEvent.id).label('count')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(TrackingEvent.is_ai_bot).all()
        
        # Daily bot types distribution
        daily_bot_types = self.db.query(
            func.date(TrackingEvent.timestamp).label('date'),
            TrackingEvent.is_ai_bot,
            func.count(TrackingEvent.id).label('count')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(func.date(TrackingEvent.timestamp), TrackingEvent.is_ai_bot).all()
        
        # Convert daily bot types to dictionary format
        daily_bot_types_dict = {}
        for date, bot_type, count in daily_bot_types:
            date_str = date.isoformat()
            if date_str not in daily_bot_types_dict:
                daily_bot_types_dict[date_str] = {}
            daily_bot_types_dict[date_str][bot_type] = count
        
        return {
            'bot_types': {bot_type: count for bot_type, count in bot_types},
            'daily_bot_types': daily_bot_types_dict,
            'period_days': days
        }
    
    def get_recent_events(self, site_id: str, limit: int = 10) -> List[TrackingEvent]:
        """Get recent events for a site - only AI bots."""
        return self.db.query(TrackingEvent).filter(
            TrackingEvent.site_id == site_id
        ).order_by(desc(TrackingEvent.timestamp)).limit(limit).all()
    
    def delete_old_events(self, days: int = 90) -> int:
        """Delete events older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = self.db.query(TrackingEvent).filter(
            TrackingEvent.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted_count