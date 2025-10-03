"""Server-side AI bot detection endpoint."""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.api.deps import get_db
from app.services.ai_detection_service import AIBotDetectionService
from app.services.tracking_service import TrackingEventService
from app.models.tracking import TrackingEvent
from app.utils.logging import log_tracking_event

router = APIRouter()


@router.post("/server-detection")
async def server_detection(request: Request, db: Session = Depends(get_db)):
    """Receive AI bot detection requests from user's servers."""
    
    try:
        data = await request.json()
        
        # Extract data
        site_id = data.get('site_id')
        ip_address = data.get('ip_address')
        user_agent = data.get('user_agent')
        url = data.get('url', '')
        referrer = data.get('referrer', '')
        
        if not site_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="site_id is required"
            )
        
        # Log incoming request
        print(f"🖥️  SERVER DETECTION: Site={site_id} | IP={ip_address} | UA={user_agent[:60] if user_agent else 'None'}... | Time={datetime.now().strftime('%H:%M:%S')}")
        print("-" * 80)
        
        # Detect AI bot
        bot_category, bot_name, detection_method = AIBotDetectionService.detect_ai_bot_comprehensive(
            user_agent, ip_address, db
        )
        
        if bot_category:
            # AI bot detected - save event
            tracking_service = TrackingEventService(db)
            
            tracking_event = TrackingEvent(
                site_id=site_id,
                event_type='server_detection',
                url=url,
                path=data.get('url_path', ''),
                title=f'AI Bot Detection - {bot_name}',
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address,
                is_ai_bot=bot_category,
                bot_name=bot_name,
                detection_method=detection_method,
                timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
            )
            
            db.add(tracking_event)
            db.commit()
            
            # Log successful detection
            log_tracking_event(
                event_type='server_detection',
                site_id=site_id,
                ip_address=ip_address,
                user_agent=user_agent,
                is_ai_bot=True,
                bot_name=bot_name
            )
            
            print(f"🎯 SERVER DETECTION: AI Bot {bot_name} detected and logged!")
            print(f"📊 DETAILS: Site={site_id} | IP={ip_address} | Method={detection_method}")
            print(f"💾 SAVED TO: Database + Logs")
            print("=" * 60)
            
            return {
                "status": "detected",
                "is_ai_bot": True,
                "bot_name": bot_name,
                "bot_category": bot_category,
                "detection_method": detection_method,
                "message": f"AI bot {bot_name} detected"
            }
        
        else:
            # Not an AI bot
            print(f"👤 HUMAN VISITOR: Site={site_id} | IP={ip_address} | UA={user_agent[:50] if user_agent else 'None'}...")
            print(f"ℹ️  STATUS: Not an AI bot - event ignored")
            print("=" * 60)
            
            return {
                "status": "human",
                "is_ai_bot": False,
                "bot_name": None,
                "bot_category": None,
                "detection_method": None,
                "message": "Human visitor - not logged"
            }
            
    except Exception as e:
        error_message = f"Server detection error: {str(e)}"
        print(f"❌ SERVER DETECTION ERROR: {e}")
        print("=" * 60)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.options("/server-detection")
async def options_server_detection():
    """Handle CORS preflight for server detection."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, User-Agent",
            "Access-Control-Max-Age": "86400",
        }
    )
