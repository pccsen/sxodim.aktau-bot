from sqlalchemy import Column, Integer, ForeignKey
from .base import BaseModel

class Favorite(BaseModel):
    __tablename__ = "favorites"
    user_id = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False) 