from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.database import Base
from datetime import datetime


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)   # در دیاگرام UNIQUE و INDEX دارد
    password_hash = Column(String, nullable=False)
    created_at = Column(String, nullable=True)
    # نقش حساب: "admin" دسترسی کامل، "user" دسترسی محدود به اطلاعات خودش
    role = Column(String, nullable=False, default="admin")
    # برای حساب‌های user، به مشتری مربوطه اشاره می‌کند (برای admin خالی است)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)