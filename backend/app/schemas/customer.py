from pydantic import BaseModel
from typing import Optional


class CustomerBase(BaseModel):
    name: str
    phone_number: str 
    notes: Optional[str] = None
    address: Optional[str] = None
    register_date: Optional[str] = None


class CustomerCreate(CustomerBase):
    # اطلاعات حساب کاربری مرتبط (اختیاری). اگر پر شوند یک حساب با نقش user ساخته می‌شود.
    username: Optional[str] = None
    password: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    notes: Optional[str] = None
    address: Optional[str] = None
    register_date: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    # نام کاربری حساب مرتبط (اگر وجود داشته باشد) تا فرم ویرایش بتواند آن را نمایش دهد
    username: Optional[str] = None
    has_account: bool = False

    class Config:
        from_attributes = True
