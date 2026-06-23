from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models import Customer, Line, Reservation, WorkSchedule

router = APIRouter(prefix="/api", tags=["Dashboard"])


def require_auth(request: Request):
    if not request.session.get("admin_id"):
        return False
    return True


@router.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    # تعدادهای کلی
    total_services = db.query(Line).count() 
    total_line_types = db.query(func.count(func.distinct(Line.name_line))).scalar() or 0  # تعداد اسم‌های لاین منحصر به فرد        
    total_customers = db.query(Customer).count()
    total_reservations = db.query(Reservation).count()

    # درآمد کل (از رزروهای موفق)
    total_revenue = db.query(func.sum(Reservation.total_price)).filter(
        Reservation.status.in_(["confirmed", "completed"])
    ).scalar() or 0

    # محبوب‌ترین سرویس بر اساس تعداد scheduleهای busy
    most_popular_service = (
        db.query(
            Line.id,
            Line.name_line,
            Line.name_service,
            func.count(WorkSchedule.id).label("busy")
        )
        .join(WorkSchedule, Line.id == WorkSchedule.line_id)
        .filter(WorkSchedule.status == "busy")
        .group_by(Line.id, Line.name_line, Line.name_service)
        .order_by(func.count(WorkSchedule.id).desc())
        .first()
    )

    # آخرین رزروها
    recent_reservations = (
        db.query(Reservation)
        .options(joinedload(Reservation.customer), joinedload(Reservation.line))
        .order_by(Reservation.id.desc())
        .limit(5)
        .all()
    )

    return {
        "total_services": total_services,  
        "total_line_types": total_line_types,         
        "total_customers": total_customers,
        "total_reservations": total_reservations,
        "total_revenue": round(float(total_revenue), 2),
        
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