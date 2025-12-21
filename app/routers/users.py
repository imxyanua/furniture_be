from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.user import UserResponse, UserUpdate
from ..schemas.product import ReviewSchema
from ..models.user import User
from ..models.review import Review
from ..services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.address is not None:
        current_user.address = user_update.address
    if user_update.img is not None:
        current_user.img = user_update.img
    if user_update.birth_date is not None:
        current_user.birth_date = user_update.birth_date
    if user_update.gender is not None:
        current_user.gender = user_update.gender
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/reviews", response_model=List[ReviewSchema])
def get_my_reviews(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return reviews
