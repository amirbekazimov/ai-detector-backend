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
    
    // Version 2.0 - Fixed duplicate events
    console.log('AI_DETECTOR v2.0 loading...');
    
    // Prevent multiple initializations
    if (window.AI_DETECTOR_INITIALIZED) {{
        console.log('AI_DETECTOR already initialized, skipping');
        return;
    }}
    window.AI_DETECTOR_INITIALIZED = true;
    
    // AI Detector Tracking Script
    var AI_DETECTOR = {{
        siteId: '{site_id}',
        apiUrl: '{settings.API_URL}/api/v1/tracking',
        queue: [],
        isOnline: navigator.onLine,
        sentEvents: new Set(), // Track sent events to prevent duplicates
        eventCounter: 0, // Counter for unique event IDs
        initialized: false, // Prevent multiple initializations
        
        // Initialize tracking
        init: function() {{
            if (this.initialized) {{
                console.log('AI_DETECTOR already initialized, skipping init');
                return;
            }}
            this.initialized = true;
            console.log('AI_DETECTOR initializing...');
            
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
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                event_id: ++this.eventCounter // Add unique event ID
            }};
            
            console.log('Sending page_view event:', data.event_id);
            this.sendData(data);
        }},
        
        // Setup event listeners
        setupEventListeners: function() {{
            var self = this;
            
            console.log('Setting up event listeners - TEST MODE: Only page_view events');
            
            // TEST MODE: Disable all extra events to get only +1 count
            // All visibilitychange, beforeunload, and click events are disabled
            
            // Track online/offline status only
            window.addEventListener('online', function() {{
                self.isOnline = true;
                self.processQueue();
            }});
            
            window.addEventListener('offline', function() {{
                self.isOnline = false;
            }});
            
            console.log('Event listeners setup complete - only page_view will be tracked');
        }},
        
        // Track custom event
        trackEvent: function(eventType, data) {{
            var eventData = {{
                site_id: this.siteId,
                event_type: eventType,
                url: window.location.href,
                timestamp: new Date().toISOString(),
                event_id: ++this.eventCounter, // Add unique event ID
                data: data || {{}}
            }};
            
            this.sendData(eventData);
        }},
        
        // Send data to server
        sendData: function(data) {{
            // Create unique event key using event_id instead of timestamp
            var eventKey = data.event_type + '_' + data.event_id + '_' + data.url;
            
            // Check if event already sent
            if (this.sentEvents.has(eventKey)) {{
                console.log('Event already sent, skipping:', eventKey);
                return; // Already sent, skip
            }}
            
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
                        // Success - mark as sent
                        self.sentEvents.add(eventKey);
                        console.log('Event sent successfully:', eventKey);
                    }} else {{
                        // Failed, add to queue for retry
                        self.queue.push(data);
                        console.log('Event failed, added to queue:', eventKey);
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
                // Check if event already sent before processing queue
                var eventKey = data.event_type + '_' + data.event_id + '_' + data.url;
                if (!self.sentEvents.has(eventKey)) {{
                    self.sendData(data);
                }} else {{
                    console.log('Queued event already sent, skipping:', eventKey);
                }}
            }});
        }},
        
        // Flush queue before page unload
        flushQueue: function() {{
            if (this.queue.length === 0) {{
                return;
            }}
            
            // Filter out already sent events before batch sending
            var self = this;
            var unsentEvents = this.queue.filter(function(data) {{
                var eventKey = data.event_type + '_' + data.event_id + '_' + data.url;
                return !self.sentEvents.has(eventKey);
            }});
            
            if (unsentEvents.length === 0) {{
                console.log('No unsent events to flush');
                return;
            }}
            
            console.log('Flushing', unsentEvents.length, 'unsent events');
            var data = JSON.stringify(unsentEvents);
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
    
    # Return with no-cache headers to prevent browser caching
    response = Response(content=js_snippet, media_type="application/javascript")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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
        
        # Check if event was saved (only AI bots are saved)
        if event is None:
            print(f"Event ignored - not an AI bot (User-Agent: {data.get('user_agent', 'unknown')})")
            return Response(
                content=json.dumps({
                    "status": "ignored", 
                    "message": "Event ignored - not an AI bot", 
                    "is_ai_bot": False
                }),
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    "Content-Type": "application/json"
                }
            )
        
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
        
        # Log error
        log_error(
            error_message=error_message,
            error_details=str(e),
            site_id=data.get('site_id') if 'data' in locals() else None
        )
        
        return Response(
            content=json.dumps({
                "status": "error", 
                "message": "Failed to process event"
            }),
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Content-Type": "application/json"
            }
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
        error_message = f"Error processing batch tracking events: {str(e)}"
        print(error_message)
        
        # Log error
        log_error(
            error_message=error_message,
            error_details=str(e)
        )
        
        return Response(
            content=json.dumps({
                "status": "error", 
                "message": "Failed to process batch events"
            }),
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Content-Type": "application/json"
            }
        )