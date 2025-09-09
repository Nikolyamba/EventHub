from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date, time

from sqlalchemy.orm import Session

from database.session import get_db
from models import User
from models.event_models import EventType, Event, EventOrganizer
from routes.jwt_auth import get_current_user

e_router = APIRouter()

class FullEvent(BaseModel):
    description: Optional[str] = None
    type: EventType
    city: str
    date: date
    time: time

@e_router.post("/event", response_model=FullEvent)
async def create_event(data: FullEvent, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        new_event = Event(description=data.description,
                          type=data.type,
                          city=data.city,
                          date=data.date,
                          time=data.time)
        db.add(new_event)
        db.flush()
        db.refresh(new_event)
        new_organizer = EventOrganizer(user_id = user.id,
                                       event_id=new_event.id)
        db.add(new_organizer)
        db.commit()
        return new_event
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")