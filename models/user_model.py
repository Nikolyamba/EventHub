from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Enum

from database.session import Base

class UserRole(PyEnum):
    common_user = "common_user"
    organizer = "organizer"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), auto_increment=True, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), unique=False, nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.common_user)

