from sqlalchemy import Column, String, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class CategoryStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    img = Column(String(500), nullable=True)
    status = Column(Enum(CategoryStatus), default=CategoryStatus.active)

    # Relationships
    items = relationship("CategoryItem", back_populates="category", cascade="all, delete-orphan")


class CategoryItem(Base):
    __tablename__ = "category_items"

    id = Column(String(50), primary_key=True, index=True)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    img = Column(String(500), nullable=True)
    status = Column(Enum(CategoryStatus), default=CategoryStatus.active)

    # Relationships
    category = relationship("Category", back_populates="items")
    products = relationship("Product", back_populates="category_item")
