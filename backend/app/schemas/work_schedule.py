from pydantic import BaseModel
from typing import Optional

class WorkScheduleBase(BaseModel):
    line_name: str
    weekday: str
    start_time: str
    end_time: str
    status: Optional[str] = "free"

class WorkScheduleCreate(WorkScheduleBase):
    pass

class WorkScheduleUpdate(BaseModel):
    line_name: Optional[str] = None
    weekday: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None

class WorkScheduleResponse(WorkScheduleBase):
    id: int
    name_line: Optional[str] = None        # از جدول lines
     
    class Config:
        from_attributes = True
