from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON, Enum 
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base
import enum


class ProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    out_of_stock = "out_of_stock"


class Product(Base):
    __tablename__ = "products"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    img = Column(String(500), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProductStatus), default=ProductStatus.active)
    category_id = Column(String(50), ForeignKey("category_items.id"), nullable=True)
    material = Column(JSON, nullable=True)
    size = Column(JSON, nullable=True)
    root_price = Column(Float, default=0)
    current_price = Column(Float, default=0)
    review_avg = Column(Float, default=0)
    sell_count = Column(Float, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    category_item = relationship("CategoryItem", back_populates="products")
    product_items = relationship("ProductItem", back_populates="product", cascade="all, delete-orphan")
    
    # ✅ QUAN TRỌNG: Thêm lazy="noload" để KHÔNG tự động load reviews
    reviews = relationship("Review", back_populates="product", lazy="noload")


class ProductItem(Base):
    __tablename__ = "product_items"

    id = Column(String(50), primary_key=True, index=True)
    product_id = Column(String(50), ForeignKey("products.id"), nullable=False)
    color = Column(JSON, nullable=True)
    img = Column(JSON, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="product_items")