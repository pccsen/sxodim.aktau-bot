from sqlalchemy import Column, String, Text, DateTime, Boolean
from .base import BaseModel

class Promotion(BaseModel):
    __tablename__ = "promotions"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    venue = Column(String(200))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True) 