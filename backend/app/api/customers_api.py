import hashlib
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Customer, Admin
from app.api.deps import get_current_account, require_admin, is_admin
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["Customers"])

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


def hash_password(password: str) -> str:
    """هش کردن رمز عبور با همان روش auth (sha256)"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_linked_account(db: Session, customer_id: int) -> Admin:
    """حساب کاربری (role=user) مرتبط با این مشتری را برمی‌گرداند (یا None)."""
    return (
        db.query(Admin)
        .filter(Admin.customer_id == customer_id, Admin.role == "user")
        .first()
    )


def serialize_customer(db: Session, c: Customer) -> CustomerResponse:
    """ساخت پاسخ مشتری به همراه اطلاعات حساب کاربری مرتبط."""
    account = get_linked_account(db, c.id)
    return CustomerResponse(
        id=c.id,
        name=c.name,
        phone_number=c.phone_number,
        register_date=c.register_date,
        notes=c.notes or "",
        address=c.address or "",
        username=account.username if account else None,
        has_account=account is not None,
    )


def ensure_username_available(db: Session, username: str, exclude_id: int = None):
    """بررسی یکتا بودن نام کاربری در جدول admins."""
    query = db.query(Admin).filter(Admin.username == username)
    if exclude_id is not None:
        query = query.filter(Admin.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=400, detail="این نام کاربری قبلاً استفاده شده است")


@router.get("")
async def list_customers(
    request: Request,
    sort: str = Query("default"),
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
    account: Admin = Depends(get_current_account),
):
    # کاربر عادی فقط اطلاعات خودش را می‌بیند
    query = db.query(Customer)
    if not is_admin(account):
        query = query.filter(Customer.id == account.customer_id)
    customers = query.all()
    
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
        "customers": [serialize_customer(db, c) for c in paginated_customers],
    }


@router.post("/register", status_code=201)
async def register_customer(
    request: Request, body: CustomerCreate, db: Session = Depends(get_db),
):
    """ثبت‌نام عمومی مشتری (بدون نیاز به لاگین ادمین).

    اطلاعات مشتری در جدول customers و حساب کاربری با نقش user در جدول admins ذخیره می‌شود.
    """
    customer_data = body.model_dump()
    username = (customer_data.pop("username", None) or "").strip() or None
    password = (customer_data.pop("password", None) or "").strip() or None

    # برای ثبت‌نام، نام کاربری و رمز عبور الزامی هستند
    if not username or not password:
        raise HTTPException(status_code=400, detail="نام کاربری و رمز عبور الزامی است")

    ensure_username_available(db, username)

    if not customer_data.get('register_date'):
        customer_data['register_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    c = Customer(**customer_data)
    db.add(c)
    db.commit()
    db.refresh(c)

    new_account = Admin(
        username=username,
        password_hash=hash_password(password),
        role="user",
        customer_id=c.id,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    db.add(new_account)
    db.commit()

    return serialize_customer(db, c)


@router.get("/{customer_id}")
async def get_customer(
    request: Request, customer_id: int, db: Session = Depends(get_db),
    account: Admin = Depends(get_current_account),
):
    # کاربر عادی فقط اجازه دیدن رکورد خودش را دارد
    if not is_admin(account) and customer_id != account.customer_id:
        raise HTTPException(status_code=403, detail="Access denied")

    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    return serialize_customer(db, c)


@router.post("", status_code=201)
async def create_customer(
    request: Request, body: CustomerCreate, db: Session = Depends(get_db),
    account: Admin = Depends(require_admin),
):
    # تبدیل data به دیکشنری و جدا کردن فیلدهای حساب کاربری
    customer_data = body.model_dump()
    username = (customer_data.pop("username", None) or "").strip() or None
    password = (customer_data.pop("password", None) or "").strip() or None

    # اگر قرار است حساب ساخته شود، ابتدا یکتا بودن نام کاربری را بررسی کن
    if username:
        ensure_username_available(db, username)

    # اگر register_date ارسال نشده، از زمان حال استفاده کن
    if not customer_data.get('register_date'):
        customer_data['register_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    c = Customer(**customer_data)
    db.add(c)
    db.commit()
    db.refresh(c)

    # ساخت حساب کاربری مرتبط (role=user) در جدول admins
    if username and password:
        new_account = Admin(
            username=username,
            password_hash=hash_password(password),
            role="user",
            customer_id=c.id,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        db.add(new_account)
        db.commit()

    return serialize_customer(db, c)


@router.put("/{customer_id}")
async def update_customer(
    request: Request, customer_id: int, body: CustomerCreate,
    db: Session = Depends(get_db),
    account: Admin = Depends(get_current_account),
):
    # کاربر عادی فقط اجازه ویرایش رکورد خودش را دارد
    if not is_admin(account) and customer_id != account.customer_id:
        raise HTTPException(status_code=403, detail="Access denied")

    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    c.name = body.name
    c.phone_number = body.phone_number
    if hasattr(body, 'notes'):
        c.notes = body.notes
    if hasattr(body, 'address'):
        c.address = body.address

    # مدیریت حساب کاربری مرتبط
    username = (body.username or "").strip() or None
    password = (body.password or "").strip() or None
    linked = get_linked_account(db, c.id)

    if linked:
        # به‌روزرسانی نام کاربری در صورت تغییر
        if username and username != linked.username:
            ensure_username_available(db, username, exclude_id=linked.id)
            linked.username = username
        # به‌روزرسانی رمز عبور فقط اگر مقدار جدیدی وارد شده باشد
        if password:
            linked.password_hash = hash_password(password)
    elif username and password:
        # ساخت حساب جدید اگر قبلاً وجود نداشته باشد
        ensure_username_available(db, username)
        db.add(Admin(
            username=username,
            password_hash=hash_password(password),
            role="user",
            customer_id=c.id,
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        ))

    db.commit()
    db.refresh(c)

    return serialize_customer(db, c)


@router.patch("/{customer_id}")
async def patch_customer(
    request: Request, customer_id: int, body: CustomerUpdate,
    db: Session = Depends(get_db),
    account: Admin = Depends(get_current_account),
):
    # کاربر عادی فقط اجازه ویرایش رکورد خودش را دارد
    if not is_admin(account) and customer_id != account.customer_id:
        raise HTTPException(status_code=403, detail="Access denied")

    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    data = body.model_dump(exclude_unset=True)
    # فیلدهای حساب کاربری را جدا از فیلدهای مشتری پردازش کن
    username = data.pop("username", None)
    password = data.pop("password", None)

    for key, val in data.items():
        setattr(c, key, val)

    # مدیریت حساب کاربری مرتبط
    username = (username or "").strip() or None
    password = (password or "").strip() or None
    if username or password:
        linked = get_linked_account(db, c.id)
        if linked:
            if username and username != linked.username:
                ensure_username_available(db, username, exclude_id=linked.id)
                linked.username = username
            if password:
                linked.password_hash = hash_password(password)
        elif username and password:
            ensure_username_available(db, username)
            db.add(Admin(
                username=username,
                password_hash=hash_password(password),
                role="user",
                customer_id=c.id,
                created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ))

    db.commit()
    db.refresh(c)

    return serialize_customer(db, c)


@router.delete("/{customer_id}")
async def delete_customer(
    request: Request, customer_id: int, db: Session = Depends(get_db),
    account: Admin = Depends(require_admin),
):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    # حذف حساب‌های کاربری مرتبط (رعایت کلید خارجی customer_id در جدول admins)
    linked_accounts = db.query(Admin).filter(Admin.customer_id == customer_id).all()
    for acc in linked_accounts:
        db.delete(acc)

    db.delete(c)
    db.commit()
    return {"message": "Customer deleted successfully"}