from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


# Revenue Report
class RevenueByPeriod(BaseModel):
    date: str  # YYYY-MM-DD for daily, YYYY-MM for monthly, YYYY for yearly
    total_orders: int
    total_revenue: float
    total_products_sold: int


class RevenueReport(BaseModel):
    period: str  # daily, monthly, yearly
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    total_revenue: float
    total_orders: int
    data: List[RevenueByPeriod]


# Order Detail Report
class OrderDetailItem(BaseModel):
    product_id: str
    product_name: str
    color: Optional[dict] = None
    quantity: int
    price: float
    line_total: float


class OrderDetailReport(BaseModel):
    id: str
    order_date: datetime
    customer_name: str
    customer_phone: str
    customer_address: str
    payment_method: str
    sub_total: float
    vat: float
    delivery_fee: float
    total_order: float
    items: List[OrderDetailItem]

    class Config:
        from_attributes = True


# Top Products Report
class TopProductReport(BaseModel):
    product_id: str
    product_name: str
    total_quantity_sold: int
    total_revenue: float


# Low Stock Alert
class LowStockAlert(BaseModel):
    product_id: str
    product_name: str
    quantity_available: int
    reorder_level: int
    reorder_quantity: int
    status: str  # "low_stock" or "out_of_stock"

    class Config:
        from_attributes = True
