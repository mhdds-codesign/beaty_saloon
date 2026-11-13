from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # line_name is a category/group label, not a unique key in lines.
    # Do not declare it as a PostgreSQL foreign key to lines.name_line because
    # multiple services intentionally share the same line_name (e.g. "ناخن").
    line_name = Column(String, nullable=False, index=True)
    weekday = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    status = Column(String, nullable=False, default="")

    line = relationship(
        "Line",
        primaryjoin="foreign(WorkSchedule.line_name) == Line.name_line",
        back_populates="work_schedules",
        uselist=False,
    )
    reservations = relationship("Reservation", back_populates="work_schedule")
