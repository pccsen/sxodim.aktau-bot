from sqlalchemy import Column, Integer, Text
from .base import BaseModel

class Feedback(BaseModel):
    __tablename__ = "feedback"

    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False) 