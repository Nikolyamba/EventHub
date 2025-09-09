from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from datetime import date, time

from sqlalchemy.orm import Session

from database.session import get_db
from models import User
from models.event_models import EventType, Event, EventOrganizer, EventAttend
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

@e_router.patch("/event/{event_id}", response_model=FullEvent)
async def edit_event(data: FullEvent, event_id:int, user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Такого мероприятия не существует")
        organizer = (
            db.query(EventOrganizer)
            .filter(EventOrganizer.event_id == event.id, EventOrganizer.user_id == user.id)
            .first()
        )
        if not organizer:
            raise HTTPException(status_code=403, detail="Вы не организатор этого мероприятия")
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

class EventUsersInfo(BaseModel):
    user_id: int
    class Config:
        orm_mode = True

class EventInfo(FullEvent):
    id: int
    attendees: List[EventUsersInfo]
    class Config:
        orm_mode = True

@e_router.post("/event/{event_id}", response_model=EventInfo)
async def sign_on_event(event_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Такого мероприятия не существует")
        organizer = (
            db.query(EventOrganizer)
            .filter(EventOrganizer.event_id == event.id, EventOrganizer.user_id == user.id)
            .first()
        )
        if organizer:
            raise HTTPException(status_code=409, detail="Вы организатор мероприятия и уже являетесь его участником!")
        old_member = db.query(EventAttend).filter(EventAttend.event_id == event.id, EventAttend.user_id == user.id).first()
        if old_member:
            raise HTTPException(status_code=409, detail="Вы уже зарегестрированы на мероприятие!")
        member = EventAttend(event_id = event.id,
                             user_id = user.id)
        db.add(member)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

@e_router.get("/event", response_model=List[EventInfo])
async def get_events(
            db: Session = Depends(get_db),
            city: Optional[str] = Query(None, description="Фильтр по городу"),
            type: Optional[EventType] = Query(None, description="Фильтр по типу события"),
            date: Optional[date] = Query(None, description="Фильтр по дате"),
            sort_by: Optional[str] = Query("date", description="Сортировка: date | city | type"),
            order: Optional[str] = Query("asc", description="Порядок: asc | desc")
    ):
    try:
        query = db.query(Event)

        if city:
            query = query.filter(Event.city == city)
        if type:
            query = query.filter(Event.type == type)
        if date:
            query = query.filter(Event.date == date)

        if sort_by == "city":
            order_column = Event.city
        elif sort_by == "type":
            order_column = Event.type
        else:
            order_column = Event.date

        if order == "desc":
            order_column = order_column.desc()

        events = query.order_by(order_column).all()
        return events
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")





