from sqlalchemy import Column, String, DateTime, Enum, JSON
from ..database import Base
from datetime import datetime
import enum


class BannerStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    expired = "expired"


class Banner(Base):
    __tablename__ = "banners"

    id = Column(String(50), primary_key=True, index=True)
    date_start = Column(String(50), nullable=True)
    date_end = Column(String(50), nullable=True)
    img = Column(String(500), nullable=False)
    status = Column(Enum(BannerStatus), default=BannerStatus.active)
    product = Column(JSON, nullable=True)  # ["product_id1", "product_id2"] - Match database column name
