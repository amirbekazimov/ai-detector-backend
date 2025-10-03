"""IP Range management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.api.deps import get_db
from app.services.ip_range_service import IPRangeService
from app.services.scheduler_service import scheduler_service

router = APIRouter()


@router.post("/ip-ranges/update-all")
async def update_all_ip_ranges(
    db: Session = Depends(get_db)
):
    """Update IP ranges for all AI bot sources."""
    try:
        ip_service = IPRangeService(db)
        result = await ip_service.update_all_ai_bot_ips()
        
        return {
            "message": "IP ranges update completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update IP ranges: {str(e)}"
        )


@router.post("/ip-ranges/update/{source_name}")
async def update_ip_ranges_for_source(
    source_name: str,
    db: Session = Depends(get_db)
):
    """Update IP ranges for a specific source."""
    ip_service = IPRangeService(db)
    
    if source_name not in ip_service.IP_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_name}' not found. Available sources: {list(ip_service.IP_SOURCES.keys())}"
        )
    
    try:
        source_url = ip_service.IP_SOURCES[source_name]
        result = await ip_service.update_ip_ranges_from_source(source_name, source_url)
        
        if result['success']:
            return {
                "message": f"IP ranges updated for {source_name}",
                "result": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update IP ranges: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update IP ranges: {str(e)}"
        )


@router.get("/ip-ranges/stats")
async def get_ip_range_stats(
    bot_name: str = None,
    db: Session = Depends(get_db)
):
    """Get statistics about stored IP ranges."""
    try:
        ip_service = IPRangeService(db)
        stats = ip_service.get_bot_ip_stats(bot_name)
        
        return {
            "message": "IP range statistics",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get IP range stats: {str(e)}"
        )


@router.post("/ip-ranges/test/{ip_address}")
async def test_ip_address(
    ip_address: str,
    db: Session = Depends(get_db)
):
    """Test if an IP address is detected as an AI bot."""
    try:
        ip_service = IPRangeService(db)
        is_bot, bot_name, detection_type = ip_service.is_ip_in_ai_bot_range(ip_address)
        
        return {
            "ip_address": ip_address,
            "is_ai_bot": is_bot,
            "bot_name": bot_name,
            "detection_type": detection_type,
            "message": f"IP {ip_address} {'is' if is_bot else 'is not'} detected as AI bot"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test IP address: {str(e)}"
        )


@router.get("/ip-ranges/sources")
async def get_ip_range_sources():
    """Get available IP range sources."""
    return {
        "message": "Available IP range sources",
        "sources": {
            "chatgpt_user": "ChatGPT User IP addresses",
            "gptbot": "GPTBot crawler IP addresses", 
            "searchbot": "SearchBot crawler IP addresses",
            "openai_all": "All OpenAI bot IP addresses"
        },
        "repository": "https://github.com/FabrizioCafolla/openai-crawlers-ip-ranges"
    }


@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler service status."""
    try:
        status_info = scheduler_service.get_scheduler_status()
        
        return {
            "message": "Scheduler service status",
            "status": status_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.post("/scheduler/start")
async def start_scheduler():
    """Start the scheduler service."""
    try:
        scheduler_service.start_scheduler()
        
        return {
            "message": "Scheduler started successfully",
            "status": scheduler_service.get_scheduler_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler service."""
    try:
        scheduler_service.stop_scheduler()
        
        return {
            "message": "Scheduler stopped successfully",
            "status": scheduler_service.get_scheduler_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.post("/scheduler/update-ip-now")
async def trigger_ip_update():
    """Manually trigger IP range update."""
    try:
        scheduler_service.schedule_ip_update_now()
        
        return {
            "message": "IP range update triggered",
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger IP update: {str(e)}"
        )


@router.post("/scheduler/update-chatgpt-now")
async def trigger_chatgpt_ip_update():
    """Manually trigger ChatGPT IP update from crawlers-info.de."""
    try:
        scheduler_service.schedule_chatgpt_ip_update_now()
        
        return {
            "message": "ChatGPT IP update triggered",
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger ChatGPT IP update: {str(e)}"
        )


@router.post("/ip-ranges/update-chatgpt")
async def update_chatgpt_ips(
    db: Session = Depends(get_db)
):
    """Update ChatGPT IP addresses from crawlers-info.de."""
    try:
        ip_service = IPRangeService(db)
        result = ip_service.update_chatgpt_ips_from_crawlers_info()
        
        if result['status'] == 'success':
            return {
                "message": "ChatGPT IP ranges updated successfully",
                "details": result
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Update failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update ChatGPT IPs: {str(e)}"
        )
