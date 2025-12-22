from pydantic import BaseModel
from typing import Dict


class ReviewStatsResponse(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]
    
    class Config:
        from_attributes = True
