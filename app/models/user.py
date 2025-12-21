from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone  # ✅ Thêm timezone
from ..database import Base
import enum


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    img = Column(String(500), nullable=True)
    birth_date = Column(String(50), nullable=True)
    gender = Column(String(20), nullable=True)
    date_enter = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # ✅ Fix
    status = Column(Enum(UserStatus), default=UserStatus.active)
    role = Column(Enum(UserRole), default=UserRole.user)

    # Relationships
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")