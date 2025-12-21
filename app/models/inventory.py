from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
import enum


class TransactionType(str, enum.Enum):
    import_stock = "import_stock"  # Nhập hàng từ NCC
    export_stock = "export_stock"  # Xuất hàng (bán)
    adjustment = "adjustment"       # Điều chỉnh tồn kho
    return_stock = "return_stock"   # Trả hàng


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String(50), primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False, unique=True)
    quantity_on_hand = Column(Integer, default=0)  # Số lượng tồn kho
    quantity_reserved = Column(Integer, default=0)  # Số lượng đã đặt nhưng chưa xuất
    reorder_level = Column(Integer, default=10)     # Mức cảnh báo hết hàng
    reorder_quantity = Column(Integer, default=50)  # Số lượng đề xuất nhập
    last_restock_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", backref="inventory")
    transactions = relationship("InventoryTransaction", back_populates="inventory", cascade="all, delete-orphan")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(String(50), primary_key=True, index=True)
    inventory_id = Column(String(50), ForeignKey("inventory.id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    supplier_id = Column(String(50), ForeignKey("suppliers.id"), nullable=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)  # Số lượng (+ nhập, - xuất)
    unit_cost = Column(Float, nullable=True)    # Giá nhập (cho import_stock)
    total_cost = Column(Float, nullable=True)   # Tổng tiền
    reference_number = Column(String(100), nullable=True)  # Số phiếu nhập/xuất
    note = Column(String(500), nullable=True)
    created_by = Column(String(50), nullable=True)  # User ID
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    inventory = relationship("Inventory", back_populates="transactions")
    product = relationship("Product")
    supplier = relationship("Supplier", back_populates="inventory_transactions")
