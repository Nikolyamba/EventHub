from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from database.session import Base

class UserRole(PyEnum):
    common_user = "common_user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), autoincrement=True, primary_key=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), unique=False, nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.common_user)

    organized_events = relationship("EventOrganizer", backref="user")
    attended_events = relationship("EventAttend", backref="user")