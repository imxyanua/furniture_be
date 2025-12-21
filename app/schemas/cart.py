from pydantic import BaseModel
from typing import Optional, Dict, Any


class CartItemCreate(BaseModel):
    product_id: str
    product_item_id: Optional[str] = None
    name: str
    img: Optional[str] = None
    color: Optional[Dict[str, Any]] = None  # Changed to accept JSON object
    quantity: int = 1
    price: float


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: str
    product_item_id: Optional[str] = None
    name: str
    img: Optional[str] = None
    color: Optional[Dict[str, Any]] = None  # Changed to return JSON object
    quantity: int
    price: float

    class Config:
        from_attributes = True
