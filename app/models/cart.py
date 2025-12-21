from sqlalchemy import Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from ..database import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    product_item_id = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    img = Column(String(500), nullable=True)
    color = Column(JSON, nullable=True)  # Changed to JSON type
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="cart_items")
