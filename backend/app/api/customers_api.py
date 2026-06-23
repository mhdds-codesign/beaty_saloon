from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["Customers"])


def require_auth(request: Request):
    if not request.session.get("admin_id"):
        return False
    return True

# تابع مرتب‌سازی فارسی برای نام
def persian_sort_key(customer):
    """مرتب‌سازی بر اساس نام فارسی"""
    persian_alphabet = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
    name = customer.name or ''
    
    result = []
    for char in name:
        if char in persian_alphabet:
            result.append(persian_alphabet.index(char))
        else:
            result.append(ord(char))
    return result


@router.get("")
async def list_customers(
    request: Request,
    sort: str = Query("default"),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    # دریافت همه مشتریان از دیتابیس
    customers = db.query(Customer).all()
    
    # مرتب‌سازی با استفاده از order_map + تابع فارسی
    order_map = {
        "default": lambda: sorted(customers, key=lambda x: x.id),
        "name": lambda: sorted(customers, key=persian_sort_key),  # مرتب‌سازی فارسی
        "phone": lambda: sorted(customers, key=lambda x: x.phone_number or ''),
        "register_date": lambda: sorted(customers, key=lambda x: x.register_date or '', reverse=True),
    }
    
    # اجرای مرتب‌سازی بر اساس پارامتر sort
    sorted_customers = order_map.get(sort, order_map["default"])()
    
    # صفحه‌بندی
    total = len(sorted_customers)
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_customers = sorted_customers[start:end]


    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "customers": [
            CustomerResponse(
                id=c.id,
                name=c.name,
                phone_number=c.phone_number,
                register_date=c.register_date,
                notes=c.notes or "",
                address=c.address or "",
            )
            for c in paginated_customers
        ],
    }


@router.get("/{customer_id}")
async def get_customer(
    request: Request, customer_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return CustomerResponse(
        id=c.id,
        name=c.name,
        phone_number=c.phone_number,
        register_date=c.register_date,
        notes=c.notes or "",
        address=c.address or "",
    )


@router.post("", status_code=201)
async def create_customer(
    request: Request, body: CustomerCreate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    # تبدیل data به دیکشنری
    customer_data = body.model_dump()
    
    # اگر register_date ارسال نشده، از زمان حال استفاده کن
    if not customer_data.get('register_date'):
        customer_data['register_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c = Customer(**customer_data)
    db.add(c)
    db.commit()
    db.refresh(c)
    
    return CustomerResponse(
        id=c.id,
        name=c.name,
        phone_number=c.phone_number,
        register_date=c.register_date,
        notes=c.notes or "",
        address=c.address or "",
    )


@router.put("/{customer_id}")
async def update_customer(
    request: Request, customer_id: int, body: CustomerCreate,
    db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    c.name = body.name
    c.phone_number = body.phone_number
    if hasattr(body, 'notes'):
        c.notes = body.notes
    if hasattr(body, 'address'):
        c.address = body.address
    
    db.commit()
    db.refresh(c)
    
    return CustomerResponse(
        id=c.id,
        name=c.name,
        phone_number=c.phone_number,
        register_date=c.register_date,
        notes=c.notes or "",
        address=c.address or "",
    )


@router.patch("/{customer_id}")
async def patch_customer(
    request: Request, customer_id: int, body: CustomerUpdate,
    db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(c, key, val)
    
    db.commit()
    db.refresh(c)
    
    return CustomerResponse(
        id=c.id,
        name=c.name,
        phone_number=c.phone_number,
        register_date=c.register_date,
        notes=c.notes or "",
        address=c.address or "",
    )


@router.delete("/{customer_id}")
async def delete_customer(
    request: Request, customer_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(c)
    db.commit()
    return {"message": "Customer deleted successfully"}