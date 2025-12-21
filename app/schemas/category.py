from pydantic import BaseModel
from typing import List, Optional


class CategoryItemSchema(BaseModel):
    id: str
    name: str
    img: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: str
    name: str
    img: Optional[str] = None
    status: str
    items: List[CategoryItemSchema] = []

    class Config:
        from_attributes = True
