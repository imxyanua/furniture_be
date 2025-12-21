from pydantic import BaseModel, Field
from typing import List, Optional


class CountryResponse(BaseModel):
    id: str
    name: str
    city: Optional[List[str]] = Field(None, alias="cities")

    class Config:
        from_attributes = True
        populate_by_name = True
