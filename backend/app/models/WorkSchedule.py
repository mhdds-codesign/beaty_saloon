from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class WorkSchedule(Base):
    __tablename__ = 'work_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, ForeignKey('lines.id'), nullable=True)  # INTEGER NULL
    weekday = Column(String, nullable=False)               # TEXT (در دیاگرام weekday از نوع TEXT است)
    start_time = Column(String, nullable=False)            # TEXT
    end_time = Column(String, nullable=False)              # TEXT
    status = Column(String, nullable=False, default="")                 # TEXT (در دیاگرام موجود است)

    line = relationship("Line", back_populates="work_schedules")
    reservations = relationship("Reservation", back_populates="work_schedule")