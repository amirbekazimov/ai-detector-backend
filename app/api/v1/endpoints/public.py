"""Public endpoints for client pages and AI bot detection."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from datetime import datetime
import json

router = APIRouter()


@router.get("/client-page", response_class=HTMLResponse)
async def get_client_page(
    request: Request,
    site_id: str,
    db: Session = Depends(get_db)
):
    """Serves a client page with server-side AI bot detection."""
    
    # Get client information
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Handle proxy headers
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]
    
    # Log every request for debugging
    print(f"🌐 CLIENT PAGE REQUEST: IP={client_ip} | UA={user_agent[:60]}... | Site={site_id} | Time={datetime.now().strftime('%H:%M:%S')}")
    print("-" * 80)
    
    # Import services
    from app.services.ai_detection_service import AIBotDetectionService
    from app.services.tracking_service import TrackingEventService
    from app.services.site_service import SiteService
    
    # Check if site exists
    site_service = SiteService(db)
    site = site_service.get_site_by_site_id(site_id)
    
    if not site:
        return HTMLResponse(content=f"""
        <html>
        <head><title>Site Not Found</title></head>
        <body>
            <h1>❌ Site Not Found</h1>
            <p>Site ID: {site_id}</p>
            <p>This site is not registered in our system.</p>
        </body>
        </html>
        """, status_code=404)
    
    # Server-side AI bot detection
    detection_status = "Human visitor"
    bot_info = ""
    is_ai_bot = False
    
    try:
        # Detect AI bot using comprehensive method
        bot_category, bot_name, detection_method = AIBotDetectionService.detect_ai_bot_comprehensive(
            user_agent, client_ip, db
        )
        
        if bot_category:
            is_ai_bot = True
            detection_status = f"✅ AI Bot Detected!"
            bot_info = f"Type: {bot_category} | Bot: {bot_name} | Method: {detection_method}"
            
            # Save tracking event to database
            tracking_service = TrackingEventService(db)
            event_data = {
                'site_id': site_id,
                'event_type': 'page_view',
                'url': f'{request.url}',
                'user_agent': user_agent,
                'timestamp': datetime.now().isoformat(),
                'title': f'Server-side detection for {site.name}',
                'path': '/client-page'
            }
            
            event = tracking_service.create_tracking_event(event_data, client_ip)
            if event:
                print(f"🎯 SERVER DETECTION: Event #{event.id} saved - {bot_name} detected!")
                print(f"📊 DETAILS: IP={client_ip} | UA={user_agent[:50]}... | Site={site.name}")
                print(f"💾 SAVED TO: Database + Logs")
                print("=" * 60)
            else:
                print(f"⚠️  Failed to save event for {bot_name}")
        else:
            print(f"👤 HUMAN VISITOR: IP={client_ip} | UA={user_agent[:50]}... | Site={site.name}")
            print(f"ℹ️  STATUS: Not an AI bot - event ignored")
            print("=" * 60)
            
    except Exception as e:
        detection_status = f"Error in detection: {str(e)}"
        print(f"❌ ERROR IN DETECTION: {e}")
        print("=" * 60)
    
    # Generate HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Detection - {site.name}</title>
        <meta name="description" content="AI Bot Detection Page for {site.domain}">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                line-height: 1.6;
                min-height: 100vh;
            }}
            .container {{
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .status {{
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 5px solid {'#4ade80' if is_ai_bot else '#fbbf24'};
            }}
            .info {{
                background: rgba(0,0,0,0.3);
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
            }}
            .highlight {{
                background: rgba(255,255,255,0.2);
                padding: 3px 8px;
                border-radius: 4px;
                font-family: monospace;
            }}
            .success {{ border-left-color: #4ade80; }}
            .warning {{ border-left-color: #fbbf24; }}
            h1 {{ text-align: center; margin-bottom: 30px; }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                opacity: 0.7;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Bot Detection</h1>
            
            <div class="status {'success' if is_ai_bot else 'warning'}">
                <h3>🎯 Detection Result</h3>
                <p><strong>{detection_status}</strong></p>
                {f'<p><strong>Bot Information:</strong> {bot_info}</p>' if bot_info else ''}
                <p>This page is designed to detect AI bots visiting your website.</p>
            </div>

            <div class="info">
                <h3>📊 Request Information</h3>
                <p><strong>Site:</strong> <span class="highlight">{site.name}</span></p>
                <p><strong>Domain:</strong> <span class="highlight">{site.domain}</span></p>
                <p><strong>Site ID:</strong> <span class="highlight">{site_id}</span></p>
                <p><strong>Your IP:</strong> <span class="highlight">{client_ip}</span></p>
                <p><strong>User-Agent:</strong> <span class="highlight">{user_agent[:80]}{'...' if len(user_agent) > 80 else ''}</span></p>
                <p><strong>Time:</strong> <span class="highlight">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></p>
            </div>

            <div class="info">
                <h3>🔍 Detection Methods</h3>
                <p><strong>1. User-Agent Analysis:</strong> Checks browser User-Agent for known AI bot patterns</p>
                <p><strong>2. IP Address Check:</strong> Verifies visitor IP against known AI bot IP ranges</p>
                <p><strong>3. Combined Detection:</strong> Uses both methods for maximum accuracy</p>
            </div>

            <div class="info">
                <h3>📈 What Happens Next</h3>
                {f'''
                <p>✅ <strong>AI Bot Detected!</strong> This visit has been logged in our system.</p>
                <p>📊 The site owner can view detection statistics in their dashboard.</p>
                <p>🔔 Real-time notifications are sent for AI bot visits.</p>
                ''' if is_ai_bot else '''
                <p>ℹ️ <strong>Human Visitor:</strong> This visit is not logged (only AI bots are tracked).</p>
                <p>🤖 If you're an AI bot, you should be detected automatically.</p>
                <p>🔍 Try visiting this page with different AI bots to test detection.</p>
                '''}
            </div>

            <div class="footer">
                <p>AI Detector System - Professional AI Bot Detection</p>
                <p>Powered by Advanced User-Agent + IP Address Analysis</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
