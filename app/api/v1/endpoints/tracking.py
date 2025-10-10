"""JavaScript snippet generation and tracking endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import PlainTextResponse, Response, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.api.deps import get_db
from app.services.site_service import SiteService
from app.services.tracking_service import TrackingEventService
from app.utils.logging import log_error, log_tracking_event
from app.core.config import settings
import ipaddress

router = APIRouter()


def get_real_client_ip(request: Request) -> str:
    """
    Extract real client IP address from request headers.
    Handles various proxy configurations automatically.
    """
    # List of headers to check in order of priority
    ip_headers = [
        'CF-Connecting-IP',      # Cloudflare
        'X-Forwarded-For',       # Standard proxy header
        'X-Real-IP',            # Nginx proxy
        'X-Client-IP',          # Apache proxy
        'X-Forwarded',          # Alternative
        'Forwarded-For',        # Alternative
        'Forwarded',            # RFC 7239
    ]
    
    # Check each header
    for header in ip_headers:
        if header in request.headers:
            ip_value = request.headers[header]
            
            # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2)
            if header == 'X-Forwarded-For':
                # Take the first IP (original client)
                ip_value = ip_value.split(',')[0].strip()
            
            # Validate IP address
            if is_valid_public_ip(ip_value):
                return ip_value
    
    # Fallback to direct connection IP
    direct_ip = request.client.host if request.client else "unknown"
    
    # If direct IP is private/internal, try to get from other sources
    if not is_valid_public_ip(direct_ip):
        # Check if there's any IP in headers that might be valid
        for header in ip_headers:
            if header in request.headers:
                ip_value = request.headers[header]
                if header == 'X-Forwarded-For':
                    ip_value = ip_value.split(',')[0].strip()
                
                # Return first valid IP found, even if private
                if ip_value and ip_value != "unknown":
                    return ip_value
    
    return direct_ip


def is_valid_public_ip(ip_str: str) -> bool:
    """
    Check if IP is valid and public (not private/internal).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        
        # Check if it's a private IP
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
            
        # Check if it's a valid public IP
        return not ip.is_reserved
        
    except ValueError:
        return False


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
    
    // AI Detector v3.0 - Professional AI Bot Detection
    console.log('AI_DETECTOR v3.0 loading...');
    
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
        sentEvents: new Set(),
        eventCounter: 0,
        initialized: false,
        
        // Initialize tracking
        init: function() {{
            if (this.initialized) {{
                console.log('AI_DETECTOR already initialized, skipping init');
                return;
            }}
            this.initialized = true;
            console.log('AI_DETECTOR initializing for site: {site_id}');
            
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
                event_id: ++this.eventCounter
            }};
            
            console.log('AI_DETECTOR: Sending page_view event');
            this.sendData(data);
        }},
        
        // Setup event listeners
        setupEventListeners: function() {{
            var self = this;
            
            // Track online/offline status
            window.addEventListener('online', function() {{
                self.isOnline = true;
                self.processQueue();
            }});
            
            window.addEventListener('offline', function() {{
                self.isOnline = false;
            }});
            
            console.log('AI_DETECTOR: Event listeners setup complete');
        }},
        
        // Track custom event
        trackEvent: function(eventType, data) {{
            var eventData = {{
                site_id: this.siteId,
                event_type: eventType,
                url: window.location.href,
                timestamp: new Date().toISOString(),
                event_id: ++this.eventCounter,
                data: data || {{}}
            }};
            
            this.sendData(eventData);
        }},
        
        // Send data to server
        sendData: function(data) {{
            var eventKey = data.event_type + '_' + data.event_id + '_' + data.url;
            
            if (this.sentEvents.has(eventKey)) {{
                console.log('AI_DETECTOR: Event already sent, skipping');
                return;
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
                        try {{
                            var response = JSON.parse(xhr.responseText);
                            self.sentEvents.add(eventKey);
                            
                            if (response.is_ai_bot) {{
                                console.log('AI_DETECTOR: AI Bot detected -', response.bot_name, '(' + response.detection_method + ')');
                            }} else {{
                                console.log('AI_DETECTOR: Human visitor detected');
                            }}
                        }} catch (e) {{
                            console.log('AI_DETECTOR: Event sent successfully');
                        }}
                    }} else {{
                        self.queue.push(data);
                        console.log('AI_DETECTOR: Event failed, added to queue');
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
                var eventKey = data.event_type + '_' + data.event_id + '_' + data.url;
                if (!self.sentEvents.has(eventKey)) {{
                    self.sendData(data);
                }}
            }});
        }},
        
        // Flush queue before page unload
        flushQueue: function() {{
            if (this.queue.length === 0) {{
                return;
            }}
            
            var self = this;
            var unsentEvents = this.queue.filter(function(data) {{
                var eventKey = data.event_type + '_' + data.event_id + '_' + data.url;
                return !self.sentEvents.has(eventKey);
            }});
            
            if (unsentEvents.length === 0) {{
                return;
            }}
            
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
        detection_info = f" [{event.detection_method}]" if event.detection_method else ""
        print(f"Event saved to database with ID: {event.id}{bot_info}{detection_info}")
        
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


@router.post("/detect")
async def detect_ai_bot(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Simple AI Bot Detection API - DarkVisitors style
    
    Usage:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "https://back.aidetector.velmi.ai/api/v1/tracking/detect",
                headers={
                    "Authorization": f"Bearer {YOUR_SITE_ID}",
                    "Content-Type": "application/json",
                },
                json={
                    "request_path": request.url.path,
                    "request_method": request.method,
                    "request_headers": dict(request.headers),
                }
            )
    """
    try:
        # Get site_id from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header. Use: Bearer YOUR_SITE_ID"
            )
        
        site_id = auth_header.replace("Bearer ", "").strip()
        
        # Verify site exists
        site_service = SiteService(db)
        site = site_service.get_site_by_site_id(site_id)
        
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
        
        # Get request data
        try:
            data = await request.json()
        except:
            data = {}
        
        # Get client IP with improved extraction
        client_ip = get_real_client_ip(request)
        
        # First try to get IP from request_headers in JSON data
        if "request_headers" in data and isinstance(data["request_headers"], dict):
            # Try both lowercase and capitalized versions
            forwarded_for = (data["request_headers"].get("X-Forwarded-For", "") or 
                           data["request_headers"].get("x-forwarded-for", ""))
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            else:
                real_ip = (data["request_headers"].get("X-Real-IP", "") or 
                          data["request_headers"].get("x-real-ip", ""))
                if real_ip:
                    client_ip = real_ip
        
        # Fallback to direct headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Get User-Agent from request_headers or direct header
        user_agent = ""
        if "request_headers" in data:
            if isinstance(data["request_headers"], dict):
                # Try both lowercase and capitalized versions
                user_agent = (data["request_headers"].get("user-agent", "") or 
                            data["request_headers"].get("User-Agent", ""))
            else:
                user_agent = str(data["request_headers"])
        
        if not user_agent:
            user_agent = request.headers.get("user-agent", "")
        
        # Detect AI bot
        from app.services.ai_detection_service import AIBotDetectionService
        
        print(f"🔍 AI Detection API called:")
        print(f"  📍 Site ID: {site_id}")
        print(f"  🌐 User-Agent: {user_agent[:100]}...")
        print(f"  📍 IP: {client_ip}")
        print(f"  🛣️ Path: {data.get('request_path', '/')}")
        print(f"  🔍 Searching IP {client_ip} in AI bot database...")
        
        bot_category, bot_name, detection_method = AIBotDetectionService.detect_ai_bot_comprehensive(
            user_agent=user_agent,
            ip_address=client_ip,
            db=db
        )
        
        is_ai_bot = bot_category is not None
        
        # Log detailed detection result
        if is_ai_bot:
            print(f"🚨 AI BOT DETECTED!")
            print(f"  🤖 Bot Name: {bot_name}")
            print(f"  🎯 Detection Method: {detection_method}")
            print(f"  📍 IP: {client_ip}")
            print(f"  ✅ IP {client_ip} FOUND in AI bot database")
        else:
            print(f"👤 Human visitor detected")
            print(f"  📍 IP: {client_ip}")
            print(f"  ❌ IP {client_ip} NOT FOUND in AI bot database")
        
        # Create tracking event
        tracking_service = TrackingEventService(db)
        
        # Get referrer safely
        referrer = ""
        if "request_headers" in data and isinstance(data["request_headers"], dict):
            referrer = data["request_headers"].get("referer", "")
        
        event_data = {
            "site_id": site_id,
            "event_type": "api_detection",
            "url": data.get("request_path", "/"),
            "user_agent": user_agent,
            "referrer": referrer,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        tracking_service.create_tracking_event(event_data, ip_address=client_ip)
        
        # Return detection result
        return {
            "is_ai_bot": is_ai_bot,
            "bot_name": bot_name or "None",
            "detection_method": detection_method,
            "confidence": 1.0 if is_ai_bot else 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Detection API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection failed: {str(e)}"
        )


@router.get("/test-chatgpt", response_class=HTMLResponse)
async def test_chatgpt_page(request: Request, db: Session = Depends(get_db)):
    """HTML page for ChatGPT testing - automatically runs AI detection."""
    
    # Run AI detection on server side
    from app.services.ai_detection_service import AIBotDetectionService
    
    # Get client IP and User-Agent with improved IP extraction
    client_ip = get_real_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    
    # Detect AI bot
    bot_category, bot_name, detection_method = AIBotDetectionService.detect_ai_bot_comprehensive(
        user_agent=user_agent,
        ip_address=client_ip,
        db=db
    )
    
    is_ai_bot = bot_category is not None
    
    # Log detection result
    if is_ai_bot:
        print(f"🚨 AI BOT DETECTED!")
        print(f"  🤖 Bot Name: {bot_name}")
        print(f"  🎯 Detection Method: {detection_method}")
        print(f"  📍 IP: {client_ip}")
        print(f"  ✅ IP {client_ip} FOUND in AI bot database")
    else:
        print(f"👤 Human visitor detected")
        print(f"  📍 IP: {client_ip}")
        print(f"  ❌ IP {client_ip} NOT FOUND in AI bot database")
    
    # Create HTML with detection result
    status_text = "🚨 AI BOT DETECTED!" if is_ai_bot else "👤 Human visitor detected"
    status_class = "success" if is_ai_bot else "info"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Detector Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
        .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .status {{ padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .success {{ background: #d4edda; color: #155724; }}
        .info {{ background: #d1ecf1; color: #0c5460; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Detector Test</h1>
        <div class="status {status_class}">{status_text}</div>
        <div>
            <h3>Detection Results:</h3>
            <p><strong>Bot Name:</strong> {bot_name or 'None'}</p>
            <p><strong>Method:</strong> {detection_method or 'Unknown'}</p>
            <p><strong>IP Address:</strong> {client_ip}</p>
            <p><strong>User Agent:</strong> {user_agent[:100]}...</p>
        </div>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)