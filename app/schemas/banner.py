from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import date


class BannerResponse(BaseModel):
    id: str
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    img: str
    status: str
    product: Optional[List[str]] = None  # Changed from products to product

    @field_validator('date_start', 'date_end', mode='before')
    @classmethod
    def convert_date_to_string(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return str(v)

    class Config:
        from_attributes = True
