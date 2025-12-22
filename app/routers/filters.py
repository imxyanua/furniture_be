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
        price=["Dưới 1.000.000", "1-5.000.000", "5-10.000.000", " Trên 10.000.000"],
        color={"Xám": "#808080", "Nâu": "#8B4513", "Trắng": "#FFFFFF", "Đen": "#000000", "Beige": "#F5F5DC", },
        material=["Gỗ", "Kim loại", "Vải", "Da", "Kính"],
        feature=["Điều chỉnh được", "Lưu trữ", "Gấp được", "Chống thấm nước", "Thân thiện với môi trường"],
        popular_search=["Hiện đại", "Cổ điển", "Tối giản", "Sang trọng", "Scandinavian"],
        price_range={"min": 0, "max": 10000},
        series=["Đơn giản", "Hiện đại", "Đương đại", "Truyền thống", "Công nghiệp"],
        sort_by=["Giá: Thấp đến Cao", "Giá: Cao đến Thấp", "Tên A-Z", "Mới nhất", "Đánh giá cao nhất", "Bán chạy nhất"]
    )
    