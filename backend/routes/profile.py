from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import UserResponse
import aiofiles
import os

router = APIRouter(prefix="/api/profile", tags=["profile"])

UPLOAD_DIR = "uploads/profiles"

@router.get("/", response_model=UserResponse)
async def get_profile(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/upload-photo")
async def upload_photo(
    user_id: int = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload profile photo"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate filename
    filename = f"{user_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update user photo URL
    user.photo_url = f"/uploads/profiles/{filename}"
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Photo uploaded successfully",
        "photo_url": user.photo_url
    }

@router.put("/language")
async def update_language(
    user_id: int = Query(...),
    language: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update language preference"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.language = language
    db.commit()
    db.refresh(user)
    
    return {"language": user.language}

