from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductItemSchema(BaseModel):
    id: str
    color: Optional[Dict[str, str]] = None
    img: Optional[List[str]] = None

    class Config:
        from_attributes = True


class ReviewSchema(BaseModel):
    id: str
    user_id: str
    product_id: str
    rating: float
    comment: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    img: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    category_id: Optional[str] = None
    material: Optional[Dict[str, str]] = None
    size: Optional[Dict[str, str]] = None
    root_price: float = 0
    current_price: float = 0


class ProductCreate(ProductBase):
    """Schema để tạo sản phẩm mới"""
    pass


class ProductUpdate(BaseModel):
    """Schema để cập nhật sản phẩm - tất cả fields đều optional"""
    name: Optional[str] = None
    img: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[str] = None
    material: Optional[Dict[str, str]] = None
    size: Optional[Dict[str, str]] = None
    root_price: Optional[float] = None
    current_price: Optional[float] = None


class ProductResponse(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}
    
    id: str
    name: str
    img: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: str
    category_id: Optional[str] = None
    material: Optional[Dict[str, str]] = None
    size: Optional[Dict[str, str]] = None
    root_price: float
    current_price: float
    review_avg: float
    sell_count: float
    timestamp: datetime
    items: List[ProductItemSchema] = Field(default=[], validation_alias="product_items")
    reviews: List[ReviewSchema] = []



class ReviewCreate(BaseModel):
    rating: float
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None
