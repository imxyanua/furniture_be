from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.country import CountryResponse
from ..models.country import Country

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("", response_model=List[CountryResponse])
def get_countries(db: Session = Depends(get_db)):
    countries = db.query(Country).all()
    return countries
