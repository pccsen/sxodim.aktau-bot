from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
import uvicorn
from app.bot.bot import start_bot
from app.database.database import engine
from app.models.base import Base

from app.database.database import get_db
from app.models.event import Event
from app.models.promotion import Promotion
from app.schemas.event import EventCreate, EventUpdate, EventInDB

app = FastAPI(title="Event Bot API")

@app.get("/")
async def root():
    return {"message": "Event Bot API"}

@app.post("/events/", response_model=EventInDB)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/events/", response_model=List[EventInDB])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@app.get("/events/{event_id}", response_model=EventInDB)
def read_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.put("/events/{event_id}", response_model=EventInDB)
def update_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

# Create database tables
Base.metadata.create_all(bind=engine)

async def main():
    bot_task = asyncio.create_task(start_bot())
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())
    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(main()) 