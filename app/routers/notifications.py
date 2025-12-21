from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models.notification import Notification
from ..schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationUpdate,
    UnreadCountResponse
)
from ..services.auth import get_current_user
from ..models.user import User


router = APIRouter(prefix="/notifications", tags=["notifications"])


def generate_notification_id() -> str:
    """Generate unique notification ID"""
    return f"NOTIF_{uuid.uuid4().hex[:8].upper()}"


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of notifications for current user"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    notifications = query.order_by(Notification.timestamp.desc()).offset(skip).limit(limit).all()
    return notifications


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return {"count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single notification by ID"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.put("/read-all", response_model=dict)
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read for current user"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    return {"count": count}


# Helper function to create notifications (used by other routers)
def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    type: str = "order",
    reference_id: Optional[str] = None
) -> Notification:
    """Create a new notification"""
    notification = Notification(
        id=generate_notification_id(),
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        reference_id=reference_id,
        is_read=False,
        timestamp=datetime.now()
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
