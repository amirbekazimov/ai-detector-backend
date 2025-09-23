"""User service for authentication."""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserRegister
from app.utils.security import get_password_hash, verify_password


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserRegister) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
