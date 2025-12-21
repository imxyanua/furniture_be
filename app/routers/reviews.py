from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.product import ReviewSchema, ReviewUpdate
from ..models.review import Review
from ..models.product import Product
from ..models.user import User
from ..services.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


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
    
    if review_update.star is not None:
        review.star = review_update.star
    if review_update.message is not None:
        review.message = review_update.message
    if review_update.img is not None:
        review.img = review_update.img
    if review_update.service is not None:
        review.service = review_update.service
    
    db.commit()
    db.refresh(review)
    
    # Update product review average
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if product:
        all_reviews = db.query(Review).filter(Review.product_id == review.product_id).all()
        if all_reviews:
            product.review_avg = sum(r.star for r in all_reviews) / len(all_reviews)
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
            product.review_avg = sum(r.star for r in all_reviews) / len(all_reviews)
        else:
            product.review_avg = 0
        db.commit()
    
    return None
