from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.session import get_db
from models.user_model import UserRole, User

u_router = APIRouter()

class UserRegister(BaseModel):
    login: Annotated[str, Field(min_length=8, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=50)]

@u_router.post("/users")
async def create_user(data: UserRegister, db: Session = Depends(get_db)) -> dict:
    try:
        old_user = db.query(User).filter(User.login == data.login).first()
        if old_user:
            raise HTTPException(status_code=409, detail="Пользователь с таким логином уже зарегестрирован!")
        new_user = User(login=data.login,
                        password=data.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success": True, "status_code": 201}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

