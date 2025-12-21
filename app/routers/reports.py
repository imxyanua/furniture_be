from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import List, Optional
from datetime import datetime, date
from ..database import get_db
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..models.inventory import Inventory
from ..schemas.report import (
    RevenueReport,
    RevenueByPeriod,
    OrderDetailReport,
    OrderDetailItem,
    TopProductReport,
    LowStockAlert
)
from ..services.auth import require_admin
from ..models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/revenue", response_model=RevenueReport)
def get_revenue_report(
    period: str = Query(..., regex="^(daily|monthly|yearly)$"),
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Báo cáo doanh thu theo ngày/tháng/năm
    - period: daily, monthly, yearly
    - from_date: YYYY-MM-DD (optional)
    - to_date: YYYY-MM-DD (optional)
    """
    query = db.query(Order)
    
    # Filter by date range
    if from_date:
        query = query.filter(Order.timestamp >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Order.timestamp <= datetime.fromisoformat(to_date))
    
    orders = query.all()
    
    # Group by period
    revenue_data = {}
    
    for order in orders:
        if period == "daily":
            key = order.timestamp.strftime("%Y-%m-%d")
        elif period == "monthly":
            key = order.timestamp.strftime("%Y-%m")
        else:  # yearly
            key = order.timestamp.strftime("%Y")
        
        if key not in revenue_data:
            revenue_data[key] = {
                "total_orders": 0,
                "total_revenue": 0,
                "total_products_sold": 0
            }
        
        revenue_data[key]["total_orders"] += 1
        revenue_data[key]["total_revenue"] += order.total_order
        
        # Count products sold
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        revenue_data[key]["total_products_sold"] += sum(item.quantity for item in items)
    
    # Convert to list
    data_list = [
        RevenueByPeriod(
            date=date_key,
            total_orders=data["total_orders"],
            total_revenue=data["total_revenue"],
            total_products_sold=data["total_products_sold"]
        )
        for date_key, data in sorted(revenue_data.items())
    ]
    
    # Calculate totals
    total_revenue = sum(d.total_revenue for d in data_list)
    total_orders = sum(d.total_orders for d in data_list)
    
    return RevenueReport(
        period=period,
        from_date=from_date,
        to_date=to_date,
        total_revenue=total_revenue,
        total_orders=total_orders,
        data=data_list
    )


@router.get("/orders/{order_id}", response_model=OrderDetailReport)
def get_order_detail(
    order_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xem chi tiết hóa đơn: sản phẩm, khách hàng"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get order items
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    items_list = [
        OrderDetailItem(
            product_id=item.product_id,
            product_name=item.name,
            color=item.color,
            quantity=item.quantity,
            price=item.price,
            line_total=item.quantity * item.price
        )
        for item in order_items
    ]
    
    return OrderDetailReport(
        id=order.id,
        order_date=order.timestamp,
        customer_name=order.full_name,
        customer_phone=order.phone,
        customer_address=f"{order.address}, {order.city}, {order.country}",
        payment_method=order.payment_method,
        sub_total=order.sub_total,
        vat=order.vat,
        delivery_fee=order.delivery_fee,
        total_order=order.total_order,
        items=items_list
    )


@router.get("/orders", response_model=List[OrderDetailReport])
def get_all_orders(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    customer_name: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xem tất cả hóa đơn với filter"""
    query = db.query(Order)
    
    if from_date:
        query = query.filter(Order.timestamp >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Order.timestamp <= datetime.fromisoformat(to_date))
    if customer_name:
        query = query.filter(Order.full_name.ilike(f"%{customer_name}%"))
    
    orders = query.order_by(Order.timestamp.desc()).limit(limit).all()
    
    result = []
    for order in orders:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        items_list = [
            OrderDetailItem(
                product_id=item.product_id,
                product_name=item.name,
                color=item.color,
                quantity=item.quantity,
                price=item.price,
                line_total=item.quantity * item.price
            )
            for item in order_items
        ]
        
        result.append(OrderDetailReport(
            id=order.id,
            order_date=order.timestamp,
            customer_name=order.full_name,
            customer_phone=order.phone,
            customer_address=f"{order.address}, {order.city}, {order.country}",
            payment_method=order.payment_method,
            sub_total=order.sub_total,
            vat=order.vat,
            delivery_fee=order.delivery_fee,
            total_order=order.total_order,
            items=items_list
        ))
    
    return result


@router.get("/top-products", response_model=List[TopProductReport])
def get_top_products(
    limit: int = 10,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Top sản phẩm bán chạy"""
    query = db.query(
        OrderItem.product_id,
        Product.name,
        func.sum(OrderItem.quantity).label("total_quantity"),
        func.sum(OrderItem.quantity * OrderItem.price).label("total_revenue")
    ).join(Product).join(Order)
    
    if from_date:
        query = query.filter(Order.timestamp >= datetime.fromisoformat(from_date))
    if to_date:
        query = query.filter(Order.timestamp <= datetime.fromisoformat(to_date))
    
    results = query.group_by(OrderItem.product_id, Product.name)\
                   .order_by(func.sum(OrderItem.quantity).desc())\
                   .limit(limit)\
                   .all()
    
    return [
        TopProductReport(
            product_id=r.product_id,
            product_name=r.name,
            total_quantity_sold=r.total_quantity,
            total_revenue=r.total_revenue
        )
        for r in results
    ]


@router.get("/low-stock", response_model=List[LowStockAlert])
def get_low_stock_alerts(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cảnh báo sản phẩm sắp hết hàng"""
    inventories = db.query(Inventory).join(Product).all()
    
    alerts = []
    for inv in inventories:
        quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        
        if quantity_available <= 0:
            status = "out_of_stock"
        elif quantity_available <= inv.reorder_level:
            status = "low_stock"
        else:
            continue
        
        alerts.append(LowStockAlert(
            product_id=inv.product_id,
            product_name=inv.product.name,
            quantity_available=quantity_available,
            reorder_level=inv.reorder_level,
            reorder_quantity=inv.reorder_quantity,
            status=status
        ))
    
    return sorted(alerts, key=lambda x: x.quantity_available)
