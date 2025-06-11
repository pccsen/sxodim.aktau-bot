from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    date = Column(DateTime, nullable=False)
    location = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    venue = Column(String(200))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self, db_url="sqlite:///bot.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_event(self, title, description, date, location):
        event = Event(
            title=title,
            description=description,
            date=date,
            location=location
        )
        self.session.add(event)
        self.session.commit()
        return event

    def get_upcoming_events(self, limit=5):
        return self.session.query(Event)\
            .filter(Event.date >= datetime.utcnow())\
            .order_by(Event.date)\
            .limit(limit)\
            .all()

    def get_event(self, event_id):
        return self.session.query(Event).filter_by(id=event_id).first()

    def update_event(self, event_id, **kwargs):
        event = self.get_event(event_id)
        if event:
            for key, value in kwargs.items():
                setattr(event, key, value)
            self.session.commit()
            return True
        return False

    def delete_event(self, event_id):
        event = self.get_event(event_id)
        if event:
            self.session.delete(event)
            self.session.commit()
            return True
        return False

    def add_promotion(self, title, description, venue, start_date, end_date):
        promotion = Promotion(
            title=title,
            description=description,
            venue=venue,
            start_date=start_date,
            end_date=end_date
        )
        self.session.add(promotion)
        self.session.commit()
        return promotion

    def get_active_promotions(self):
        now = datetime.utcnow()
        return self.session.query(Promotion)\
            .filter(Promotion.start_date <= now)\
            .filter(Promotion.end_date >= now)\
            .filter(Promotion.is_active == True)\
            .all()

    def add_feedback(self, user_id, message):
        feedback = Feedback(
            user_id=user_id,
            message=message
        )
        self.session.add(feedback)
        self.session.commit()
        return feedback

    def get_all_events(self):
        return self.session.query(Event).order_by(Event.date).all()

    def get_all_promotions(self):
        return self.session.query(Promotion).order_by(Promotion.start_date).all() 