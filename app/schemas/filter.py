from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class FilterResponse(BaseModel):
    id: str
    category: Optional[str] = None
    price: Optional[List[str]] = None
    color: Optional[Dict[str, str]] = None
    material: Optional[List[str]] = None
    feature: Optional[List[str]] = None
    popular_search: Optional[List[str]] = None
    price_range: Optional[Dict[str, Any]] = None
    series: Optional[List[str]] = None
    sort_by: Optional[List[str]] = None

    class Config:
        from_attributes = True
