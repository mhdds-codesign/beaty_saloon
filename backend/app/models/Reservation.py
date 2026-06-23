from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime,Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, ForeignKey('lines.id'), nullable=False)       # INTEGER NULL
    schedule_id = Column(Integer, ForeignKey('work_schedules.id'), nullable=False)  # INTEGER NULL (مطابق دیاگرام)
    total_price = Column(Float, nullable=False, default=0.0)          
    status = Column(String, nullable=False, default="confrimed")                # TEXT
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)  # INTEGER NULL

    customer = relationship("Customer", back_populates="reservations")
    line = relationship("Line", back_populates="reservations")
    work_schedule = relationship("WorkSchedule", back_populates="reservations")