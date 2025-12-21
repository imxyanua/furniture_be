from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    contact_person = Column(String(100), nullable=True)
    tax_code = Column(String(50), nullable=True)
    bank_account = Column(String(100), nullable=True)
    bank_name = Column(String(100), nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_transactions = relationship("InventoryTransaction", back_populates="supplier")
