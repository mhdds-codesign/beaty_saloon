from pydantic import BaseModel
from typing import Optional


class LineBase(BaseModel):
    name_line: str
    duration_minutes: int = 60
    price: float
    name_service: str


class LineCreate(LineBase):
    pass


class LineUpdate(BaseModel):
    name_line: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    name_service: Optional[str] = None


class LineResponse(LineBase):
    id: int

    class Config:
        from_attributes = True
