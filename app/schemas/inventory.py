from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Inventory Schemas
class InventoryBase(BaseModel):
    product_id: str
    quantity_on_hand: int = 0
    quantity_reserved: int = 0
    reorder_level: int = 10
    reorder_quantity: int = 50


class InventoryResponse(BaseModel):
    id: str
    product_id: str
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int  # quantity_on_hand - quantity_reserved
    reorder_level: int
    reorder_quantity: int
    is_low_stock: bool  # True nếu quantity_available <= reorder_level
    last_restock_date: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryUpdate(BaseModel):
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None


# Transaction Schemas
class InventoryTransactionCreate(BaseModel):
    product_id: str
    supplier_id: Optional[str] = None
    transaction_type: str  # import_stock, export_stock, adjustment, return_stock
    quantity: int
    unit_cost: Optional[float] = None
    reference_number: Optional[str] = None
    note: Optional[str] = None


class InventoryTransactionResponse(BaseModel):
    id: str
    inventory_id: str
    product_id: str
    product_name: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    transaction_type: str
    quantity: int
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    reference_number: Optional[str] = None
    note: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
