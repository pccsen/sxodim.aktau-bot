from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    title: Optional[str] = None
    date: Optional[datetime] = None

class EventInDB(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 