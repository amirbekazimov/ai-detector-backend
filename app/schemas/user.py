"""Pydantic schemas for API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    """User in database base schema."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    """User schema for API responses."""
    pass


class UserInDB(UserInDBBase):
    """User schema for database."""
    hashed_password: str


class DetectionBase(BaseModel):
    """Base detection schema."""
    text_content: str
    ai_probability: float
    confidence_score: float
    model_used: str


class DetectionCreate(DetectionBase):
    """Detection creation schema."""
    pass


class DetectionUpdate(BaseModel):
    """Detection update schema."""
    text_content: Optional[str] = None
    ai_probability: Optional[float] = None
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None


class DetectionInDBBase(DetectionBase):
    """Detection in database base schema."""
    id: int
    user_id: Optional[int] = None
    processing_time: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Detection(DetectionInDBBase):
    """Detection schema for API responses."""
    pass


class DetectionInDB(DetectionInDBBase):
    """Detection schema for database."""
    pass
