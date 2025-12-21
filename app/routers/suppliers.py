from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from ..database import get_db
from ..models.supplier import Supplier
from ..schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from ..services.auth import require_admin
from ..models.user import User
from ..utils.helpers import generate_id

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierResponse])
def get_suppliers(
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách nhà cung cấp (Admin only)"""
    query = db.query(Supplier)
    
    if search:
        query = query.filter(
            or_(
                Supplier.name.ilike(f"%{search}%"),
                Supplier.email.ilike(f"%{search}%"),
                Supplier.phone.ilike(f"%{search}%")
            )
        )
    
    suppliers = query.order_by(Supplier.name).all()
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xem chi tiết nhà cung cấp"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Tạo nhà cung cấp mới"""
    # Check if supplier with same name exists
    existing = db.query(Supplier).filter(Supplier.name == supplier_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Supplier with this name already exists")
    
    new_supplier = Supplier(
        id=generate_id("SUP"),
        name=supplier_data.name,
        email=supplier_data.email,
        phone=supplier_data.phone,
        address=supplier_data.address,
        contact_person=supplier_data.contact_person,
        tax_code=supplier_data.tax_code,
        bank_account=supplier_data.bank_account,
        bank_name=supplier_data.bank_name,
        note=supplier_data.note
    )
    
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    
    return new_supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin nhà cung cấp"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Update fields
    update_dict = supplier_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(supplier, key, value)
    
    db.commit()
    db.refresh(supplier)
    
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa nhà cung cấp"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    db.delete(supplier)
    db.commit()
    
    return None
