from datetime import datetime
from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Reservation, Customer, Line, WorkSchedule
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationStatusUpdate, ReservationResponse

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


def require_auth(request: Request):
    if not request.session.get("admin_id"):
        return False
    return True


def reservation_to_response(r: Reservation) -> ReservationResponse:
    schedule = getattr(r, 'schedule', None)
    line = getattr(r, 'line', None)
    
    return ReservationResponse(
        id=r.id,
        line_id=r.line_id,
        customer_id=r.customer_id,
        schedule_id=r.schedule_id,
        name_line=line.name_line if line else None,
        name_service=line.name_service if line else None,
        price=r.total_price,
        customer_name=r.customer.name if r.customer else None,
        weekday=schedule.weekday if schedule else None,
        start_time=schedule.start_time if schedule else None,
        end_time=schedule.end_time if schedule else None,
        status=r.status,
    )


# ==================== تایم‌های آزاد (برای فرم ایجاد و آپدیت) ====================
@router.get("/available-slots")
async def get_available_slots(
    request: Request,
    line_id: int = Query(None),
    db: Session = Depends(get_db),
):
    """فقط اسلات‌هایی که free هستند — برای نمایش در dropdown"""
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    query = db.query(WorkSchedule).filter(WorkSchedule.status == "free")

    if line_id is not None:
        query = query.filter(WorkSchedule.line_id == line_id)

    slots = query.all()

    return {
        "success": True,
        "slots": [
            {
                "id": s.id,
                "line_id": s.line_id,
                "weekday": s.weekday,
                "start_time": s.start_time,
                "end_time": s.end_time,
            }
            for s in slots
        ]
    }


# ==================== لیست رزروها ====================
@router.get("")
async def list_reservations(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db),
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    query = db.query(Reservation)
    if status:
        query = query.filter(Reservation.status == status)

    total = query.count()
    reservations = (
        db.query(Reservation)
        .options(joinedload(Reservation.customer), joinedload(Reservation.line), joinedload(Reservation.schedule))
        .order_by(Reservation.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "reservations": [reservation_to_response(r) for r in reservations],
    }


@router.get("/{reservation_id}")
async def get_reservation(
    request: Request, reservation_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    reservation = (
        db.query(Reservation)
        .options(joinedload(Reservation.customer), joinedload(Reservation.line), joinedload(Reservation.schedule))
        .filter(Reservation.id == reservation_id)
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return reservation_to_response(reservation)


@router.post("", status_code=201)
async def create_reservation(
    request: Request, body: ReservationCreate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    customer = db.query(Customer).filter(Customer.id == body.customer_id).first()
    if not customer: raise HTTPException(404, "Customer not found")

    line = db.query(Line).filter(Line.id == body.line_id).first()
    if not line: raise HTTPException(404, "Line not found")

    schedule = db.query(WorkSchedule).filter(WorkSchedule.id == body.schedule_id).first()
    if not schedule: raise HTTPException(404, "Schedule not found")
    if schedule.status != "free":
        raise HTTPException(400, "This time slot is not available")

    reservation = Reservation(
        customer_id=body.customer_id,
        line_id=body.line_id,
        schedule_id=body.schedule_id,
        total_price=line.price,
        status=body.status,
    )
    db.add(reservation)

    schedule.status = "busy"        # تغییر وضعیت تایم به busy

    db.commit()
    db.refresh(reservation)

    # Reload for response
    reservation = db.query(Reservation).options(
        joinedload(Reservation.customer), joinedload(Reservation.line), joinedload(Reservation.schedule)
    ).filter(Reservation.id == reservation.id).first()

    return reservation_to_response(reservation)


@router.put("/{reservation_id}")
async def update_reservation(
    request: Request, reservation_id: int, body: ReservationUpdate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    old_schedule_id = reservation.schedule_id
    update_data = body.model_dump(exclude_unset=True)

    # اگر schedule_id عوض شده باشد
    new_schedule_id = update_data.get("schedule_id")
    if new_schedule_id and new_schedule_id != old_schedule_id:
        # آزاد کردن تایم قبلی
        old_schedule = db.query(WorkSchedule).filter(WorkSchedule.id == old_schedule_id).first()
        if old_schedule:
            old_schedule.status = "free"

        # چک کردن و رزرو کردن تایم جدید
        new_schedule = db.query(WorkSchedule).filter(WorkSchedule.id == new_schedule_id).first()
        if not new_schedule:
            raise HTTPException(404, "New schedule not found")
        if new_schedule.status != "free":
            raise HTTPException(400, "This time slot is not available")

        new_schedule.status = "busy"

    # اعمال بقیه تغییرات
    for key, value in update_data.items():
        setattr(reservation, key, value)

    db.commit()
    db.refresh(reservation)

    # Reload with relationships
    reservation = db.query(Reservation).options(
        joinedload(Reservation.customer), joinedload(Reservation.line), joinedload(Reservation.schedule)
    ).filter(Reservation.id == reservation.id).first()

    return reservation_to_response(reservation)


@router.patch("/{reservation_id}/status")
async def update_reservation_status(
    request: Request, reservation_id: int, body: ReservationStatusUpdate,
    db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    valid_statuses = {"confirmed", "completed", "cancelled"}
    if body.status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(404, "Reservation not found")

    reservation.status = body.status
    db.commit()

    reservation = db.query(Reservation).options(
        joinedload(Reservation.customer), joinedload(Reservation.line), joinedload(Reservation.schedule)
    ).filter(Reservation.id == reservation.id).first()

    return reservation_to_response(reservation)