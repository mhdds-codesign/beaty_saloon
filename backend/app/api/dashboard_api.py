from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models import Customer, Line, Reservation, WorkSchedule, Admin
from app.api.deps import get_current_account, is_admin

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    account: Admin = Depends(get_current_account),
):
    admin_view = is_admin(account)

    # تعدادهای غیرحساس (برای همه نمایش داده می‌شوند)
    total_services = db.query(Line).count()
    total_line_types = db.query(func.count(func.distinct(Line.name_line))).scalar() or 0  # تعداد اسم‌های لاین منحصر به فرد

    # محبوب‌ترین سرویس بر اساس تعداد scheduleهای busy
    most_popular_service = (
        db.query(
            Line.id,
            Line.name_line,
            Line.name_service,
            func.count(WorkSchedule.id).label("busy_slots")
        )
        .join(WorkSchedule, Line.name_line == WorkSchedule.line_name)
        .filter(WorkSchedule.status == "busy")
        .group_by(Line.id, Line.name_line, Line.name_service)
        .order_by(func.count(WorkSchedule.id).desc())
        .first()
    )

    # آخرین رزروها — برای کاربر عادی فقط رزروهای خودش
    recent_query = (
        db.query(Reservation)
        .options(joinedload(Reservation.customer), joinedload(Reservation.line))
    )
    if not admin_view:
        recent_query = recent_query.filter(Reservation.customer_id == account.customer_id)

    recent_reservations = recent_query.order_by(Reservation.id.desc()).limit(5).all()

    result = {
        "role": account.role,
        "total_services": total_services,
        "total_line_types": total_line_types,

        "most_popular_service": {
            "id": most_popular_service.id if most_popular_service else None,
            "name_line": most_popular_service.name_line if most_popular_service else None,
            "name_service": most_popular_service.name_service if most_popular_service else None,
            "busy_slots": most_popular_service.busy_slots if most_popular_service else 0,
        } if most_popular_service else None,

        "recent_reservations": [
            {
                "id": r.id,
                "customer_name": r.customer.name if r.customer else "نامشخص",
                "line_name": r.line.name_line if r.line else "نامشخص",
                "service_name": r.line.name_service if r.line else "نامشخص",
                "total_price": float(r.total_price),
                "status": r.status,
            }
            for r in recent_reservations
        ],
    }

    # آمار حساس فقط برای admin: درآمد، تعداد کل مشتریان و نوبت‌ها
    if admin_view:
        total_customers = db.query(Customer).count()
        total_reservations = db.query(Reservation).count()
        total_revenue = db.query(func.sum(Reservation.total_price)).filter(
            Reservation.status.in_(["confirmed", "completed"])
        ).scalar() or 0

        result["total_customers"] = total_customers
        result["total_reservations"] = total_reservations
        result["total_revenue"] = round(float(total_revenue), 2)

    return result