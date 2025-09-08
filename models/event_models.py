from sqlalchemy import Column, Integer, String, Enum, Date, Time
from enum import Enum as PyEnum
from database.session import Base

class EventType(PyEnum):
    sports = "sports"
    educational = "educational"
    entertainment = "entertainment"
    musical = "musical"

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer(), autoincrement=True, primary_key=True)
    description = Column(String(500), nullable=True)
    type = Column(Enum(EventType, name="event_type"), nullable=False)
    city = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)