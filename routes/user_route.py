from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import bcrypt
from database.session import get_db
from models.user_model import User
from routes.jwt_auth import create_access_token, create_refresh_token, get_current_user, r

u_router = APIRouter()

def hashed_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class UserRegister(BaseModel):
    login: Annotated[str, Field(min_length=8, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=50)]
    email: Annotated[str, Field(max_length=50)]


@u_router.post("/users")
async def create_user(data: UserRegister, db: Session = Depends(get_db)) -> dict:
    try:
        old_user = db.query(User).filter(User.login == data.login).first()
        if old_user:
            raise HTTPException(status_code=409, detail="Пользователь с таким логином уже зарегестрирован!")
        new_user = User(login=data.login,
                        password=hashed_password(data.password),
                        email=data.email)
        access_token = create_access_token(data={"sub": data.login})
        refresh_token = create_refresh_token(data={"sub": data.login})
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success": True, "payload": {"access_token": access_token, "refresh_token": refresh_token}}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

@u_router.post("/users/login")
async def user_login(login: str, password: str, db: Session = Depends(get_db)) -> dict:
    try:
        user = db.query(User).filter(User.login == login, User.password == hashed_password(password)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Логин или пароль введены неправильно!")
        access_token = create_access_token(data={"sub": user.login})
        refresh_token = create_refresh_token(data={"sub": user.login})
        return {"success": True, "payload": {"access_token": access_token, "refresh_token": refresh_token}}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

@u_router.post("/refresh")
async def get_new_tokens(user: User = Depends(get_current_user)) -> dict:
    try:
        if r.exists(f"refresh_token:{user.login}"):
            access_token = create_access_token(data={"sub": user.login})
            refresh_token = create_refresh_token(data={"sub": user.login})
            return {"success": True, "payload": {"access_token": access_token, "refresh_token": refresh_token}}
        else:
            raise HTTPException(status_code=401, detail="Refresh token не найден или истёк")
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")

@u_router.post("/users/logout")
async def user_logout(user: User = Depends(get_current_user)) -> dict:
    try:
        key = f"refresh_token:{user.login}"
        if r.exists(key):
            r.delete(key)
        return {"success": True, "message": "Вы вышли из системы"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")