from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str  # 'order', 'promotion', 'system'
    reference_id: Optional[str] = None


class NotificationCreate(NotificationBase):
    user_id: str


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    timestamp: datetime

    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    is_read: bool


class UnreadCountResponse(BaseModel):
    count: int
