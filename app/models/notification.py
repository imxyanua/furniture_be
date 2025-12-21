from sqlalchemy import Column, String, Text, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum('order', 'promotion', 'system'), default='order', index=True)
    reference_id = Column(String(50), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
