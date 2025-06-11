from sqlalchemy import Column, Integer
from .base import BaseModel

class Subscriber(BaseModel):
    __tablename__ = "subscribers"
    user_id = Column(Integer, unique=True, nullable=False) 