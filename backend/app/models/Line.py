from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Line(Base):
    __tablename__ = 'lines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_line = Column(String, nullable=False)              # مطابق دیاگرام
    duration_minutes = Column(Integer, nullable=True, default=60)       # INTEGER NULL
    price = Column(Float, nullable=False, default=0.0)               
    name_service = Column(String, nullable=False)            # TEXT (در دیاگرام موجود است)

    work_schedules = relationship("WorkSchedule", back_populates="line")
    reservations = relationship("Reservation", back_populates="line")