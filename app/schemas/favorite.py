from pydantic import BaseModel
from typing import Optional


class FavoriteCreate(BaseModel):
    product_id: str
    name: str
    img: Optional[str] = None
    price: float


class FavoriteResponse(BaseModel):
    id: int
    product_id: str
    name: str
    img: Optional[str] = None
    price: float

    class Config:
        from_attributes = True
