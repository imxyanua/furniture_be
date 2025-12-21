from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.banner import BannerResponse
from ..models.banner import Banner

router = APIRouter(prefix="/banners", tags=["Banners"])


@router.get("", response_model=List[BannerResponse])
def get_banners(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Banner)
    
    if status:
        query = query.filter(Banner.status == status)
    
    banners = query.offset(skip).limit(limit).all()
    return banners
