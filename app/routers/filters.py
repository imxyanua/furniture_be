from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..schemas.filter import FilterResponse
from ..models.filter import Filter

router = APIRouter(prefix="/filters", tags=["Filters"])


@router.get("", response_model=FilterResponse)
def get_filter(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get filter configuration for products.
    If category is provided, return category-specific filters.
    Otherwise, return general filters.
    """
    query = db.query(Filter)
    
    if category:
        # Try to find category-specific filter first
        filter_config = query.filter(Filter.category == category).first()
        if filter_config:
            return filter_config
    
    # Return default/general filter
    default_filter = query.filter(Filter.category.is_(None)).first()
    if default_filter:
        return default_filter
    
    # If no filter exists, return a basic default
    return FilterResponse(
        id="default",
        category=category,
        price=["Under $100", "$100-$500", "$500-$1000", "Over $1000"],
        color={"Gray": "#808080", "Brown": "#8B4513", "White": "#FFFFFF", "Black": "#000000"},
        material=["Wood", "Metal", "Fabric", "Leather", "Glass"],
        feature=["Adjustable", "Storage", "Foldable", "Waterproof"],
        popular_search=["Modern", "Vintage", "Minimalist", "Luxury"],
        price_range={"min": 0, "max": 10000},
        series=["Classic", "Modern", "Contemporary", "Traditional"],
        sort_by=["Price: Low to High", "Price: High to Low", "Name", "Newest", "Best Review"]
    )
