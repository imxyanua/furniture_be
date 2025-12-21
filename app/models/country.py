from sqlalchemy import Column, String, JSON
from ..database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cities = Column(JSON, nullable=True)  # ["City1", "City2"]
