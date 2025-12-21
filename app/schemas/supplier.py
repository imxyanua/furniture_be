from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Supplier Schemas
class SupplierBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    tax_code: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    note: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    tax_code: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    note: Optional[str] = None


class SupplierResponse(SupplierBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
