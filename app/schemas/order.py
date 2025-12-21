from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class OrderItemSchema(BaseModel):
    product_id: str
    name: str
    img: Optional[str] = None
    color: Optional[Dict] = None
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    full_name: str
    phone: str
    country: str
    city: str
    address: str
    note: Optional[str] = None
    payment_method: str
    sub_total: float
    vat: float = 0
    delivery_fee: float = 0
    total_order: float
    items: List[OrderItemSchema]


class OrderResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: str
    country: str
    city: str
    address: str
    note: Optional[str] = None
    date_order: datetime
    payment_method: str
    status_payment: str
    sub_total: float
    vat: float
    delivery_fee: float
    total_order: float
    status_order: str

    class Config:
        from_attributes = True


class OrderWithItemsResponse(BaseModel):
    order: OrderResponse
    items: List[OrderItemSchema]
