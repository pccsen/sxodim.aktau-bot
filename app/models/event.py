from sqlalchemy import Column, String, Text, DateTime
from .base import BaseModel

class Event(BaseModel):
    __tablename__ = "events"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    date = Column(DateTime, nullable=False)
    location = Column(String(200)) 