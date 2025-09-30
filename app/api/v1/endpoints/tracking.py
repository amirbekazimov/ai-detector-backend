"""JavaScript snippet generation and tracking endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.api.deps import get_db
from app.services.site_service import SiteService
from app.services.tracking_service import TrackingEventService
from app.utils.logging import log_error, log_tracking_event
from app.core.config import settings

router = APIRouter()


@router.get("/{site_id}.js", response_class=PlainTextResponse)
async def get_js_snippet(
    site_id: str,
    db: Session = Depends(get_db)
):
    """Generate JavaScript snippet for site tracking."""
    site_service = SiteService(db)
    site = site_service.get_site_by_site_id(site_id)
    
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Generate JavaScript snippet
    js_snippet = f"""
(function() {{
    'use strict';
    
    // AI Detector Tracking Script
    var AI_DETECTOR = {{
        siteId: '{site_id}',
        apiUrl: '{settings.API_URL}/api/v1/tracking',
        queue: [],
        isOnline: navigator.onLine,
        
        // Initialize tracking
        init: function() {{
            this.trackPageView();
            this.setupEventListeners();
            this.processQueue();
        }},
        
        // Track page view
        trackPageView: function() {{
            var data = {{
                site_id: this.siteId,
                event_type: 'page_view',
                url: window.location.href,
                path: window.location.pathname,
                title: document.title,
                referrer: document.referrer,
                user_agent: navigator.userAgent,
                timestamp: new Date().toISOString(),
                screen_resolution: screen.width + 'x' + screen.height,
                viewport_size: window.innerWidth + 'x' + window.innerHeight,
                language: navigator.language,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            }};
            
            this.sendData(data);
        }},
        
        // Setup event listeners
        setupEventListeners: function() {{
            var self = this;
            
            // Track page visibility changes
            document.addEventListener('visibilitychange', function() {{
                if (document.hidden) {{
                    self.trackEvent('page_hidden');
                }} else {{
                    self.trackEvent('page_visible');
                }}
            }});
            
            // Track before page unload
            window.addEventListener('beforeunload', function() {{
                self.trackEvent('page_unload');
                self.flushQueue();
            }});
            
            // Track online/offline status
            window.addEventListener('online', function() {{
                self.isOnline = true;
                self.processQueue();
            }});
            
            window.addEventListener('offline', function() {{
                self.isOnline = false;
            }});
            
            // Track clicks (optional)
            document.addEventListener('click', function(e) {{
                if (e.target.tagName === 'A') {{
                    self.trackEvent('link_click', {{
                        href: e.target.href,
                        text: e.target.textContent.trim()
                    }});
                }}
            }});
        }},
        
        // Track custom event
        trackEvent: function(eventType, data) {{
            var eventData = {{
                site_id: this.siteId,
                event_type: eventType,
                url: window.location.href,
                timestamp: new Date().toISOString(),
                data: data || {{}}
            }};
            
            this.sendData(eventData);
        }},
        
        // Send data to server
        sendData: function(data) {{
            if (!this.isOnline) {{
                this.queue.push(data);
                return;
            }}
            
            var self = this;
            var xhr = new XMLHttpRequest();
            
            xhr.open('POST', this.apiUrl + '/events', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onreadystatechange = function() {{
                if (xhr.readyState === 4) {{
                    if (xhr.status >= 200 && xhr.status < 300) {{
                        // Success
                    }} else {{
                        // Failed, add to queue for retry
                        self.queue.push(data);
                    }}
                }}
            }};
            
            xhr.send(JSON.stringify(data));
        }},
        
        // Process queued data
        processQueue: function() {{
            if (!this.isOnline || this.queue.length === 0) {{
                return;
            }}
            
            var self = this;
            var queue = this.queue.slice();
            this.queue = [];
            
            queue.forEach(function(data) {{
                self.sendData(data);
            }});
        }},
        
        // Flush queue before page unload
        flushQueue: function() {{
            if (this.queue.length === 0) {{
                return;
            }}
            
            var data = JSON.stringify(this.queue);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', this.apiUrl + '/events/batch', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(data);
        }}
    }};
    
    // Start tracking when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', function() {{
            AI_DETECTOR.init();
        }});
    }} else {{
        AI_DETECTOR.init();
    }}
    
    // Expose global object for manual tracking
    window.AI_DETECTOR = AI_DETECTOR;
}})();
""".strip()
    
    return js_snippet


@router.options("/events")
async def options_tracking_event():
    """Handle CORS preflight for tracking events."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "86400",
        }
    )


@router.post("/events")
async def receive_tracking_event(
    request: Request,
    db: Session = Depends(get_db)
):
    """Receive tracking events from JavaScript snippet."""
    try:
        data = await request.json()
        
        # Get client IP address
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
        
        # Log the event
        print(f"Tracking event received from IP {client_ip}: {json.dumps(data, indent=2)}")
        
        # Save to database with AI bot detection
        tracking_service = TrackingEventService(db)
        event = tracking_service.create_tracking_event(data, ip_address=client_ip)
        
        # Log tracking event
        log_tracking_event(
            event_type=event.event_type,
            site_id=event.site_id,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            is_ai_bot=event.is_ai_bot is not None,
            bot_name=event.bot_name
        )
        
        bot_info = f" (AI Bot: {event.bot_name})" if event.is_ai_bot else " (Human visitor)"
        print(f"Event saved to database with ID: {event.id}{bot_info}")
        
        return Response(
            content=json.dumps({
                "status": "success", 
                "message": "Event received and saved", 
                "event_id": event.id,
                "is_ai_bot": event.is_ai_bot is not None,
                "bot_name": event.bot_name
            }),
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        error_message = f"Error processing tracking event: {str(e)}"
        print(error_message)
        log_error(
            error_message=error_message,
            error_details=str(e),
            site_id=data.get('site_id') if 'data' in locals() else None
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tracking data"
        )


@router.options("/events/batch")
async def options_batch_tracking_events():
    """Handle CORS preflight for batch tracking events."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "86400",
        }
    )


@router.post("/events/batch")
async def receive_batch_tracking_events(
    request: Request,
    db: Session = Depends(get_db)
):
    """Receive batch tracking events from JavaScript snippet."""
    try:
        data = await request.json()
        
        # Get client IP address
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
        
        # Log the batch events
        print(f"Batch tracking events received from IP {client_ip}: {len(data)} events")
        for event in data:
            print(f"  - {event.get('event_type', 'unknown')}: {event.get('url', 'no url')}")
        
        # Save to database with AI bot detection
        tracking_service = TrackingEventService(db)
        events = tracking_service.create_batch_tracking_events(data, ip_address=client_ip)
        
        ai_bot_count = sum(1 for event in events if event.is_ai_bot)
        human_count = len(events) - ai_bot_count
        
        print(f"Batch events saved to database: {len(events)} events ({ai_bot_count} AI bots, {human_count} humans)")
        
        return Response(
            content=json.dumps({
                "status": "success", 
                "message": f"Received and saved {len(data)} events", 
                "events_count": len(events),
                "ai_bot_count": ai_bot_count,
                "human_count": human_count
            }),
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        print(f"Error processing batch tracking events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid batch tracking data"
        )
