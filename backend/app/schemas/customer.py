from pydantic import BaseModel
from typing import Optional


class CustomerBase(BaseModel):
    name: str
    phone_number: str 
    notes: str
    address: str


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True
