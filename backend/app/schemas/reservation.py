from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReservationCreate(BaseModel):
    line_id: int
    customer_id: int
    schedule_id: int
    status: str = "confirmed"          # وضعیت پیش‌فرض


class ReservationUpdate(BaseModel):
    line_id: Optional[int] = None
    customer_id: Optional[int] = None
    schedule_id: Optional[int] = None
    status: Optional[str] = None


class ReservationStatusUpdate(BaseModel):
    """آپدیت فقط وضعیت (ساده‌تر)"""
    status: str


class ReservationResponse(BaseModel):
    id: int
    
    # Foreign Keys
    line_id: int
    customer_id: int
    schedule_id: int

    # اطلاعات غنی شده از جداول مرتبط
    name_line: Optional[str] = None
    name_service: Optional[str] = None
    price: float


    customer_name: Optional[str] = None
    
    # اطلاعات زمانی
    weekday: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True