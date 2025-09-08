from sqlalchemy import Column, Integer, String, Enum, Date, Time, ForeignKey
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

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
    organizers = relationship("EventOrganizer", backref='event')
    attendees = relationship("EventAttend", backref='event')

class EventOrganizer(Base):
    __tablename__ = "event_organizers"
    id = Column(Integer(), autoincrement=True, primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    event_id = Column(Integer(), ForeignKey('events.id'))

class EventAttend(Base):
    __tablename__ = "event_attendees"
    id = Column(Integer(), autoincrement=True, primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.id'))
    event_id = Column(Integer(), ForeignKey('events.id'))