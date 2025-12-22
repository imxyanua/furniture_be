from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from typing import List, Optional
from ..database import get_db
from ..schemas.product import ReviewSchema, ReviewUpdate
from ..schemas.review import ReviewStatsResponse
from ..models.review import Review
from ..models.product import Product
from ..models.user import User
from ..services.auth import get_current_user, require_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])


# ===== ADMIN ENDPOINTS =====

@router.get("", response_model=List[ReviewSchema])
def get_all_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    product_id: Optional[str] = None,
    user_id: Optional[str] = None,
    min_star: Optional[float] = Query(None, ge=0, le=5),
    max_star: Optional[float] = Query(None, ge=0, le=5),
    sort_by: str = Query("timestamp", regex="^(timestamp|star)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Get all reviews with filtering and sorting"""
    query = db.query(Review)
    
    # Apply filters
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    if min_star is not None:
        query = query.filter(Review.rating >= min_star)
    if max_star is not None:
        query = query.filter(Review.rating <= max_star)
    
    # Apply sorting
    if sort_by == "star":
        query = query.order_by(desc(Review.rating) if order == "desc" else asc(Review.rating))
    else:  # timestamp
        query = query.order_by(desc(Review.timestamp) if order == "desc" else asc(Review.timestamp))
    
    # Apply pagination
    reviews = query.offset(skip).limit(limit).all()
    return reviews


@router.delete("/{review_id}/admin", status_code=204)
def admin_delete_review(
    review_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Delete any review"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    product_id = review.product_id
    db.delete(review)
    db.commit()
    
    # Update product review average
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
        if all_reviews:
            product.review_avg = sum(r.rating for r in all_reviews) / len(all_reviews)
        else:
            product.review_avg = 0
        db.commit()
    
    return None


@router.get("/stats/summary", response_model=ReviewStatsResponse)
def get_review_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin only: Get review statistics"""
    total_reviews = db.query(func.count(Review.id)).scalar()
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0.0
    
    # Count reviews by star rating
    rating_distribution = {}
    for star in range(1, 6):
        count = db.query(func.count(Review.id)).filter(
            Review.rating >= star,
            Review.rating < star + 1
        ).scalar()
        rating_distribution[f"{star}_star"] = count
    
    return {
        "total_reviews": total_reviews,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": rating_distribution
    }


# ===== USER ENDPOINTS =====

@router.patch("/{review_id}", response_model=ReviewSchema)
def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if review_update.rating is not None:
        review.rating = review_update.rating
    if review_update.comment is not None:
        review.comment = review_update.comment
    
    db.commit()
    db.refresh(review)
    
    # Update product review average
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if product:
        all_reviews = db.query(Review).filter(Review.product_id == review.product_id).all()
        if all_reviews:
            product.review_avg = sum(r.rating for r in all_reviews) / len(all_reviews)
            db.commit()
    
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    product_id = review.product_id
    db.delete(review)
    db.commit()
    
    # Update product review average
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        all_reviews = db.query(Review).filter(Review.product_id == product_id).all()
        if all_reviews:
            product.review_avg = sum(r.rating for r in all_reviews) / len(all_reviews)
        else:
            product.review_avg = 0
        db.commit()
    
    return None
