"""Detection endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import Detection, DetectionCreate
from app.services.detection_service import DetectionService

router = APIRouter()


@router.post("/detect", response_model=Detection)
async def detect_ai_content(
    detection_data: DetectionCreate,
    db: Session = Depends(get_db)
):
    """Detect AI-generated content."""
    try:
        detection_service = DetectionService(db)
        result = await detection_service.create_detection(detection_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection failed: {str(e)}"
        )


@router.get("/detections", response_model=List[Detection])
async def get_detections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all detections."""
    detection_service = DetectionService(db)
    return detection_service.get_detections(skip=skip, limit=limit)


@router.get("/detections/{detection_id}", response_model=Detection)
async def get_detection(
    detection_id: int,
    db: Session = Depends(get_db)
):
    """Get specific detection by ID."""
    detection_service = DetectionService(db)
    detection = detection_service.get_detection(detection_id)
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )
    return detection
