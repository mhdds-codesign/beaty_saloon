from pydantic import BaseModel
from typing import Optional

class WorkScheduleBase(BaseModel):
    line_id: int
    weekday: str
    start_time: str
    end_time: str
    status: Optional[str] = "free"

class WorkScheduleCreate(WorkScheduleBase):
    pass

class WorkScheduleUpdate(BaseModel):
    line_id: Optional[int] = None
    weekday: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None

class WorkScheduleResponse(WorkScheduleBase):
    id: int
    name_line: Optional[str] = None        # از جدول lines
    name_service_name: Optional[str] = None
     
    class Config:
        from_attributes = True