from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, UserResponse, UserUpdate
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=UserResponse)
async def login(
    telegram_id: str = Query(...),
    first_name: str = Query(None),
    last_name: str = Query(None),
    username: str = Query(None),
    photo_url: str = Query(None),
    db: Session = Depends(get_db)
):
    """User login via Telegram"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            photo_url=photo_url,
            balance=0.0,
            bonus_balance=10.0  # Welcome bonus
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get current user info"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_id: int = Query(...),
    update_data: UserUpdate = None,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update_data:
        if update_data.photo_url:
            user.photo_url = update_data.photo_url
        if update_data.language:
            user.language = update_data.language
        if update_data.first_name:
            user.first_name = update_data.first_name
        if update_data.last_name:
            user.last_name = update_data.last_name
    
    db.commit()
    db.refresh(user)
    return user

