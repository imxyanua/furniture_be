from sqlalchemy import Column, String, JSON
from ..database import Base


class Filter(Base):
    __tablename__ = "filters"

    id = Column(String(50), primary_key=True, index=True)
    category = Column(String(100), nullable=True)
    price = Column(JSON, nullable=True)  # ["Under $100", "$100-$500", ...]
    color = Column(JSON, nullable=True)  # {"Red": "#FF0000", "Blue": "#0000FF"}
    material = Column(JSON, nullable=True)  # ["Wood", "Metal", "Fabric"]
    feature = Column(JSON, nullable=True)  # ["Adjustable", "Storage", ...]
    popular_search = Column(JSON, nullable=True)  # ["Modern", "Vintage", ...]
    price_range = Column(JSON, nullable=True)  # {"min": 0, "max": 10000}
    series = Column(JSON, nullable=True)  # ["Classic", "Modern", ...]
    sort_by = Column(JSON, nullable=True)  # ["Price", "Name", "Date"]
