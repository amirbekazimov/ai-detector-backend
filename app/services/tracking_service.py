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
        
        # Detect AI bot
        bot_category, bot_pattern = AIBotDetectionService.detect_ai_bot(user_agent)
        bot_name = AIBotDetectionService.get_bot_name(user_agent)
        
        # Only save events from AI bots
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
            timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat()))
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        
        return db_event
    
    def create_batch_tracking_events(self, events_data: List[Dict[str, Any]], ip_address: str = None) -> List[TrackingEvent]:
        """Create multiple tracking events in batch - only for AI bots."""
        db_events = []
        
        for event_data in events_data:
            user_agent = event_data.get('user_agent')
            
            # Detect AI bot
            bot_category, bot_pattern = AIBotDetectionService.detect_ai_bot(user_agent)
            bot_name = AIBotDetectionService.get_bot_name(user_agent)
            
            # Only save events from AI bots
            if not bot_category:
                continue
            
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
                timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.now().isoformat()))
            )
            db_events.append(db_event)
        
        if db_events:
            self.db.add_all(db_events)
            self.db.commit()
            
            for event in db_events:
                self.db.refresh(event)
        
        return db_events
    
    def get_site_events(self, site_id: str, limit: int = 100, offset: int = 0) -> List[TrackingEvent]:
        """Get tracking events for a specific site."""
        return self.db.query(TrackingEvent).filter(
            TrackingEvent.site_id == site_id
        ).order_by(desc(TrackingEvent.timestamp)).offset(offset).limit(limit).all()
    
    def get_site_events_by_type(self, site_id: str, event_type: str, limit: int = 100, bot_type: str = None) -> List[TrackingEvent]:
        """Get tracking events of specific type for a site."""
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
    
    def get_daily_stats(self, site_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily statistics for a site - only AI bots."""
        since_date = datetime.now() - timedelta(days=days)
        
        # Get daily counts - all events are AI bot events
        daily_counts = self.db.query(
            func.date(TrackingEvent.timestamp).label('date'),
            func.count(TrackingEvent.id).label('total_events'),
            func.count(TrackingEvent.id).label('ai_bot_events')  # All events are AI bot events
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(func.date(TrackingEvent.timestamp)).order_by(func.date(TrackingEvent.timestamp)).all()
        
        # Format results
        daily_stats = []
        for row in daily_counts:
            daily_stats.append({
                'date': row.date.isoformat(),
                'total_events': row.total_events,
                'ai_bot_events': row.ai_bot_events,
                'human_events': 0  # No human events
            })
        
        return daily_stats
    
    def get_bot_types_stats(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """Get statistics by bot types for a site."""
        since_date = datetime.now() - timedelta(days=days)
        
        # Get bot types distribution
        bot_types = self.db.query(
            TrackingEvent.is_ai_bot,
            func.count(TrackingEvent.id).label('count')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(TrackingEvent.is_ai_bot).all()
        
        # Get daily bot types
        daily_bot_types = self.db.query(
            func.date(TrackingEvent.timestamp).label('date'),
            TrackingEvent.is_ai_bot,
            func.count(TrackingEvent.id).label('count')
        ).filter(
            and_(TrackingEvent.site_id == site_id, TrackingEvent.timestamp >= since_date)
        ).group_by(func.date(TrackingEvent.timestamp), TrackingEvent.is_ai_bot).order_by(func.date(TrackingEvent.timestamp)).all()
        
        # Format daily data
        daily_data = {}
        for row in daily_bot_types:
            date_str = row.date.isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {}
            daily_data[date_str][row.is_ai_bot] = row.count
        
        return {
            'bot_types': {bot_type: count for bot_type, count in bot_types},
            'daily_bot_types': daily_data,
            'period_days': days
        }
