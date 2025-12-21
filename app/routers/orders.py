from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.order import OrderCreate, OrderWithItemsResponse, OrderItemSchema
from ..models.order import Order, OrderItem, OrderStatus
from ..models.user import User
from ..models.product import Product
from ..services.auth import get_current_user, require_admin
from ..models.cart import CartItem
from ..utils.helpers import generate_id
from .notifications import create_notification

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderWithItemsResponse])
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"🔵 [GET /orders] User: {current_user.id}")
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(Order.date_order.desc()).all()
    
    print(f"🔵 [GET /orders] Found {len(orders)} orders")
    
    result = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        print(f"   - Order {order.id}: {order.status_order}, items: {len(items)}")
        result.append({
            "order": order,
            "items": items
        })
    
    print(f"🔵 [GET /orders] Returning {len(result)} orders")
    return result


@router.post("", status_code=200)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create order
    order_id = generate_id("ORD")
    new_order = Order(
        id=order_id,
        user_id=current_user.id,
        full_name=order_data.full_name,
        phone=order_data.phone,
        country=order_data.country,
        city=order_data.city,
        address=order_data.address,
        note=order_data.note,
        payment_method=order_data.payment_method,
        sub_total=order_data.sub_total,
        vat=order_data.vat,
        delivery_fee=order_data.delivery_fee,
        total_order=order_data.total_order
    )
    
    db.add(new_order)
    
    # Create order items
        # Create order items
    for item in order_data.items:
        # Validate price from database (security fix)
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            continue  # Skip invalid products
        
        order_item = OrderItem(
            order_id=order_id,
            product_id=item.product_id,
            name=item.name,
            img=item.img,
            color=item.color,
            quantity=item.quantity,
            price=product.current_price  # ← Changed from item.price
        )
        db.add(order_item)
        
        # Update product sell count
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.sell_count += item.quantity
    
        db.commit()
    
    # Clear cart after successful order
    try:
        deleted_count = db.query(CartItem).filter(
            CartItem.user_id == current_user.id
        ).delete()
        db.commit()
        print(f"✅ Cleared {deleted_count} cart items for user {current_user.id}")
    except Exception as e:
        print(f"⚠️ Failed to clear cart: {e}")
        # Không raise error - order đã tạo thành công rồi
    
    # Create notification for new order
    create_notification(
        db=db,
        user_id=current_user.id,
        title="Đơn hàng đã được tiếp nhận",
        message=f"Đơn hàng #{order_id} đã được đặt thành công. Tổng tiền: {order_data.total_order:,.0f}đ. Cảm ơn bạn đã mua hàng!",
        type="order",
        reference_id=order_id
    )
    
    return {"order_id": order_id}

@router.patch("/{order_id}/cancel")
def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
    
    # Only allow cancel if order is pending
    if order.status_order != "pending":
        raise HTTPException(
            status_code=400, 
            detail="Chỉ có thể hủy đơn hàng đang chờ xử lý"
        )
    
    # Update status to cancelled
    order.status_order = "cancelled"
    db.commit()
    
    # Create notification
    create_notification(
        db=db,
        user_id=current_user.id,
        title="Đơn hàng đã được hủy",
        message=f"Đơn hàng #{order_id} đã được hủy thành công.",
        type="order",
        reference_id=order_id
    )
    
    return {"message": "Đơn hàng đã được hủy thành công"}


# ADMIN ENDPOINTS

@router.get("/all", response_model=List[OrderWithItemsResponse])
def get_all_orders(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only) with optional status filter."""
    print(f"🔵 [ADMIN GET /orders/all] Admin: {current_user.id}, Status filter: {status}")
    
    query = db.query(Order).order_by(Order.date_order.desc())
    
    if status:
        query = query.filter(Order.status_order == status)
    
    orders = query.offset(offset).limit(limit).all()
    print(f"🔵 [ADMIN] Found {len(orders)} orders")
    
    result = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        result.append({
            "order": order,
            "items": items
        })
    
    return result


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: str,
    status: OrderStatus,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update order status (admin only) with validation."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
    
    # Validate status transition
    valid_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["shipping", "cancelled"],
        "shipping": ["delivered", "cancelled"],
        "delivered": [],
        "cancelled": []
    }
    
    if status.value not in valid_transitions.get(order.status_order, []):
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển trạng thái từ {order.status_order} sang {status.value}"
        )
    
    old_status = order.status_order
    order.status_order = status.value
    db.commit()
    
    # Send notification to customer
    status_messages = {
        "confirmed": "Đơn hàng đã được xác nhận",
        "shipping": "Đơn hàng đang được giao",
        "delivered": "Đơn hàng đã được giao thành công",
        "cancelled": "Đơn hàng đã bị hủy"
    }
    
    create_notification(
        db=db,
        user_id=order.user_id,
        title=status_messages.get(status.value, "Cập nhật đơn hàng"),
        message=f"Đơn hàng #{order_id} {status_messages.get(status.value, '').lower()}. Tổng tiền: {order.total_order:,.0f}đ.",
        type="order",
        reference_id=order_id
    )
    
    print(f"✅ Order {order_id} status updated: {old_status} → {status.value}")
    return {
        "message": "Cập nhật trạng thái thành công",
        "old_status": old_status,
        "new_status": status.value
    }


@router.patch("/{order_id}/confirm")
def confirm_order(
    order_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Confirm order (admin only) - shortcut for status update."""
    return update_order_status(order_id, OrderStatus.confirmed, current_user, db)


@router.patch("/{order_id}/ship")
def ship_order(
    order_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mark order as shipping (admin only) - shortcut for status update."""
    return update_order_status(order_id, OrderStatus.shipping, current_user, db)


@router.patch("/{order_id}/deliver")
def deliver_order(
    order_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mark order as delivered (admin only) - shortcut for status update."""
    return update_order_status(order_id, OrderStatus.delivered, current_user, db)