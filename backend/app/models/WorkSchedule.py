from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class WorkSchedule(Base):
    __tablename__ = 'work_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_name = Column(String, ForeignKey('lines.name_line'), nullable=False, index=True)
    weekday = Column(String, nullable=False)               # TEXT (در دیاگرام weekday از نوع TEXT است)
    start_time = Column(String, nullable=False)            # TEXT
    end_time = Column(String, nullable=False)              # TEXT
    status = Column(String, nullable=False, default="")                 # TEXT (در دیاگرام موجود است)

    line = relationship("Line", 
                       primaryjoin="foreign(WorkSchedule.line_name) == Line.name_line",
                       back_populates="work_schedules",
                       uselist=False)
    reservations = relationship("Reservation", back_populates="work_schedule")