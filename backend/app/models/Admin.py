from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database import Base
from datetime import datetime


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)   # در دیاگرام UNIQUE و INDEX دارد
    password_hash = Column(String, nullable=False)
    created_at = Column(String, nullable=True)