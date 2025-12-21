from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
import enum


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipping = "shipping"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    refunded = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    country = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    date_order = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(50), nullable=False)
    status_payment = Column(Enum(PaymentStatus), default=PaymentStatus.unpaid)
    sub_total = Column(Float, nullable=False)
    vat = Column(Float, default=0)
    delivery_fee = Column(Float, default=0)
    total_order = Column(Float, nullable=False)
    status_order = Column(Enum(OrderStatus), default=OrderStatus.pending)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    img = Column(String(500), nullable=True)
    color = Column(JSON, nullable=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
