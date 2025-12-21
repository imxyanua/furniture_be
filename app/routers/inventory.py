from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from ..database import get_db
from ..models.inventory import Inventory, InventoryTransaction, TransactionType
from ..models.product import Product
from ..models.supplier import Supplier
from ..schemas.inventory import (
    InventoryResponse, 
    InventoryUpdate,
    InventoryTransactionCreate,
    InventoryTransactionResponse
)
from ..services.auth import get_current_user, require_admin
from ..models.user import User
from ..utils.helpers import generate_id
from datetime import datetime

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryResponse])
def get_inventory(
    low_stock_only: bool = False,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xem tồn kho tất cả sản phẩm (Admin only)"""
    query = db.query(Inventory).join(Product)
    
    # Filter by search
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.id.ilike(f"%{search}%")
            )
        )
    
    inventories = query.all()
    
    result = []
    for inv in inventories:
        quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        is_low_stock = quantity_available <= inv.reorder_level
        
        # Filter low stock if requested
        if low_stock_only and not is_low_stock:
            continue
        
        result.append(InventoryResponse(
            id=inv.id,
            product_id=inv.product_id,
            product_name=inv.product.name if inv.product else None,
            product_code=inv.product.id if inv.product else None,
            quantity_on_hand=inv.quantity_on_hand,
            quantity_reserved=inv.quantity_reserved,
            quantity_available=quantity_available,
            reorder_level=inv.reorder_level,
            reorder_quantity=inv.reorder_quantity,
            is_low_stock=is_low_stock,
            last_restock_date=inv.last_restock_date,
            updated_at=inv.updated_at
        ))
    
    return result


@router.get("/{product_id}", response_model=InventoryResponse)
def get_product_inventory(
    product_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xem tồn kho của 1 sản phẩm"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    quantity_available = inventory.quantity_on_hand - inventory.quantity_reserved
    
    return InventoryResponse(
        id=inventory.id,
        product_id=inventory.product_id,
        product_name=inventory.product.name if inventory.product else None,
        product_code=inventory.product.id if inventory.product else None,
        quantity_on_hand=inventory.quantity_on_hand,
        quantity_reserved=inventory.quantity_reserved,
        quantity_available=quantity_available,
        reorder_level=inventory.reorder_level,
        reorder_quantity=inventory.reorder_quantity,
        is_low_stock=quantity_available <= inventory.reorder_level,
        last_restock_date=inventory.last_restock_date,
        updated_at=inventory.updated_at
    )


@router.patch("/{product_id}", response_model=InventoryResponse)
def update_inventory_settings(
    product_id: str,
    update_data: InventoryUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật cài đặt tồn kho (reorder level, quantity)"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    if update_data.reorder_level is not None:
        inventory.reorder_level = update_data.reorder_level
    if update_data.reorder_quantity is not None:
        inventory.reorder_quantity = update_data.reorder_quantity
    
    db.commit()
    db.refresh(inventory)
    
    quantity_available = inventory.quantity_on_hand - inventory.quantity_reserved
    
    return InventoryResponse(
        id=inventory.id,
        product_id=inventory.product_id,
        product_name=inventory.product.name if inventory.product else None,
        product_code=inventory.product.id if inventory.product else None,
        quantity_on_hand=inventory.quantity_on_hand,
        quantity_reserved=inventory.quantity_reserved,
        quantity_available=quantity_available,
        reorder_level=inventory.reorder_level,
        reorder_quantity=inventory.reorder_quantity,
        is_low_stock=quantity_available <= inventory.reorder_level,
        last_restock_date=inventory.last_restock_date,
        updated_at=inventory.updated_at
    )


@router.post("/transactions", response_model=InventoryTransactionResponse, status_code=201)
def create_inventory_transaction(
    transaction_data: InventoryTransactionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Tạo giao dịch nhập/xuất kho"""
    # Validate product
    product = db.query(Product).filter(Product.id == transaction_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get or create inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == transaction_data.product_id).first()
    if not inventory:
        inventory = Inventory(
            id=generate_id("INV"),
            product_id=transaction_data.product_id
        )
        db.add(inventory)
        db.flush()
    
    # Validate supplier if provided
    supplier_name = None
    if transaction_data.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == transaction_data.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        supplier_name = supplier.name
    
    # Calculate quantity change
    quantity_change = transaction_data.quantity
    if transaction_data.transaction_type in ["export_stock", "return_stock"]:
        quantity_change = -abs(quantity_change)
    else:
        quantity_change = abs(quantity_change)
    
    # Update inventory
    new_quantity = inventory.quantity_on_hand + quantity_change
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    inventory.quantity_on_hand = new_quantity
    
    if transaction_data.transaction_type == "import_stock":
        inventory.last_restock_date = datetime.utcnow()
    
    # Create transaction record
    total_cost = None
    if transaction_data.unit_cost:
        total_cost = transaction_data.unit_cost * abs(transaction_data.quantity)
    
    transaction = InventoryTransaction(
        id=generate_id("TRX"),
        inventory_id=inventory.id,
        product_id=transaction_data.product_id,
        supplier_id=transaction_data.supplier_id,
        transaction_type=transaction_data.transaction_type,
        quantity=quantity_change,
        unit_cost=transaction_data.unit_cost,
        total_cost=total_cost,
        reference_number=transaction_data.reference_number,
        note=transaction_data.note,
        created_by=current_user.id
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return InventoryTransactionResponse(
        id=transaction.id,
        inventory_id=transaction.inventory_id,
        product_id=transaction.product_id,
        product_name=product.name,
        supplier_id=transaction.supplier_id,
        supplier_name=supplier_name,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        unit_cost=transaction.unit_cost,
        total_cost=transaction.total_cost,
        reference_number=transaction.reference_number,
        note=transaction.note,
        created_by=transaction.created_by,
        created_at=transaction.created_at
    )


@router.get("/transactions/history", response_model=List[InventoryTransactionResponse])
def get_inventory_transactions(
    product_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xem lịch sử giao dịch nhập/xuất kho"""
    query = db.query(InventoryTransaction)
    
    if product_id:
        query = query.filter(InventoryTransaction.product_id == product_id)
    
    if transaction_type:
        query = query.filter(InventoryTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(InventoryTransaction.created_at.desc()).limit(limit).all()
    
    result = []
    for txn in transactions:
        product_name = txn.product.name if txn.product else None
        supplier_name = txn.supplier.name if txn.supplier else None
        
        result.append(InventoryTransactionResponse(
            id=txn.id,
            inventory_id=txn.inventory_id,
            product_id=txn.product_id,
            product_name=product_name,
            supplier_id=txn.supplier_id,
            supplier_name=supplier_name,
            transaction_type=txn.transaction_type,
            quantity=txn.quantity,
            unit_cost=txn.unit_cost,
            total_cost=txn.total_cost,
            reference_number=txn.reference_number,
            note=txn.note,
            created_by=txn.created_by,
            created_at=txn.created_at
        ))
    
    return result
