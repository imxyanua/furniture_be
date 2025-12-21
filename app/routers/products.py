from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from typing import List, Optional
from ..database import get_db
from ..schemas.product import ProductResponse, ReviewSchema, ReviewCreate, ReviewUpdate, ProductCreate, ProductUpdate
from ..models.product import Product
from ..models.review import Review
from ..models.user import User
from ..models.category import CategoryItem
from ..services.auth import get_current_user, require_admin
from ..utils.helpers import generate_id

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 20,
    name: Optional[str] = None,
    category_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "timestamp",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Product).options(joinedload(Product.product_items)).filter(Product.status == "active")
    
    if name:
        query = query.filter(Product.name.like(f"%{name}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.current_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.current_price <= max_price)
    
    # Sorting
    sort_column = getattr(Product, sort_by, Product.timestamp)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/special/new-arrivals", response_model=List[ProductResponse])
def get_new_arrivals(limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).options(joinedload(Product.product_items)).filter(
        Product.status == "active"
    ).order_by(desc(Product.timestamp)).limit(limit).all()
    return products


@router.get("/special/top-seller", response_model=List[ProductResponse])
def get_top_seller(limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).options(joinedload(Product.product_items)).filter(
        Product.status == "active"
    ).order_by(desc(Product.sell_count)).limit(limit).all()
    return products


@router.get("/special/best-review", response_model=List[ProductResponse])
def get_best_review(limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).options(joinedload(Product.product_items)).filter(
        Product.status == "active"
    ).order_by(desc(Product.review_avg)).limit(limit).all()
    return products


@router.get("/special/discount", response_model=List[ProductResponse])
def get_discount(limit: int = 20, db: Session = Depends(get_db)):
    products = db.query(Product).options(joinedload(Product.product_items)).filter(
        Product.status == "active",
        Product.current_price < Product.root_price
    ).order_by(desc(Product.root_price - Product.current_price)).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).options(
        joinedload(Product.product_items)
    ).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # FIX: Manually convert to response with items
    return ProductResponse.model_validate(product)


@router.get("/{product_id}/reviews", response_model=List[ReviewSchema])
def get_product_reviews(
    product_id: str,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "timestamp",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Review).filter(Review.product_id == product_id)
    
    # Map created_at to timestamp for frontend compatibility
    if sort_by == "created_at":
        sort_by = "timestamp"
    
    sort_column = getattr(Review, sort_by, Review.timestamp)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews


@router.post("/{product_id}/reviews", response_model=ReviewSchema, status_code=201)
def create_review(
    product_id: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create review
    new_review = Review(
        id=generate_id("REV"),
        product_id=product_id,
        user_id=current_user.id,
        order_id=review_data.order_id,
        star=review_data.star,
        message=review_data.message,
        img=review_data.img,
        service=review_data.service
    )
    
    db.add(new_review)
    
    # Update product review average
    all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    total_stars = sum(r.star for r in all_reviews) + review_data.star
    product.review_avg = total_stars / (len(all_reviews) + 1)
    
    db.commit()
    db.refresh(new_review)
    return new_review


# ============ PRODUCT CRUD ENDPOINTS (ADMIN ONLY) ============

@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Tạo sản phẩm mới (chỉ admin)
    """
    # Kiểm tra category tồn tại nếu có
    if product_data.category_id:
        category = db.query(CategoryItem).filter(CategoryItem.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category không tồn tại")
    
    # Tạo product mới
    new_product = Product(
        id=generate_id("PRO"),
        name=product_data.name,
        img=product_data.img,
        title=product_data.title,
        description=product_data.description,
        status=product_data.status,
        category_id=product_data.category_id,
        material=product_data.material,
        size=product_data.size,
        root_price=product_data.root_price,
        current_price=product_data.current_price,
        review_avg=0,
        sell_count=0
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Cập nhật sản phẩm (chỉ admin)
    """
    # Tìm product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    # Kiểm tra category nếu được cập nhật
    if product_data.category_id is not None:
        category = db.query(CategoryItem).filter(CategoryItem.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category không tồn tại")
    
    # Cập nhật các trường được cung cấp
    update_dict = product_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Xóa sản phẩm (chỉ admin)
    Sử dụng soft delete - chỉ đổi status thành 'inactive'
    """
    # Tìm product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    # Soft delete - đổi status thay vì xóa vĩnh viễn
    product.status = "inactive"
    
    db.commit()
    
    return None
