"""Detection service."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.user import Detection as DetectionModel
from app.schemas.user import DetectionCreate, Detection as DetectionSchema


class DetectionService:
    """Service for detection operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_detection(self, detection_data: DetectionCreate, user_id: int = None) -> DetectionSchema:
        """Create a new detection."""
        db_detection = DetectionModel(
            user_id=user_id,
            text_content=detection_data.text_content,
            ai_probability=0.75,
            confidence_score=0.85,
            model_used=detection_data.model_used,
            processing_time=0.5
        )
        
        self.db.add(db_detection)
        self.db.commit()
        self.db.refresh(db_detection)
        
        return DetectionSchema.from_orm(db_detection)
    
    def get_detections(self, skip: int = 0, limit: int = 100) -> List[DetectionSchema]:
        """Get all detections."""
        detections = self.db.query(DetectionModel).offset(skip).limit(limit).all()
        return [DetectionSchema.from_orm(detection) for detection in detections]
    
    def get_detection(self, detection_id: int) -> Optional[DetectionSchema]:
        """Get detection by ID and return it"""
        detection = self.db.query(DetectionModel).filter(DetectionModel.id == detection_id).first()
        if detection:
            return DetectionSchema.from_orm(detection)
        return None
