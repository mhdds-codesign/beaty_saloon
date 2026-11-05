from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin


def get_current_account(request: Request, db: Session = Depends(get_db)) -> Admin:
    """حساب لاگین‌شده را برمی‌گرداند (admin یا user). اگر لاگین نباشد 401."""
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    account = db.query(Admin).filter(Admin.id == admin_id).first()
    if not account:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return account


def require_admin(account: Admin = Depends(get_current_account)) -> Admin:
    """فقط برای حساب‌های admin. کاربران عادی 403 می‌گیرند."""
    if account.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return account


def is_admin(account: Admin) -> bool:
    return account.role == "admin"
