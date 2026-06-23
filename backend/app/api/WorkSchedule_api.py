from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import WorkSchedule, Line
from app.schemas.work_schedule import WorkScheduleCreate, WorkScheduleUpdate, WorkScheduleResponse

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])


def require_auth(request: Request):
    if not request.session.get("admin_id"):
        return False
    return True


def schedule_to_response(s: WorkSchedule) -> WorkScheduleResponse:
    return WorkScheduleResponse(
        id=s.id,
        line_id=s.line_id,
        weekday=s.weekday,
        start_time=s.start_time,
        end_time=s.end_time,
        status=s.status,
        line_name=getattr(s.line, 'name_line', None) if hasattr(s, 'line') and s.line else None,
    )


@router.get("")
async def list_schedules(
    request: Request,
    line_id: int = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    query = db.query(WorkSchedule)

    if line_id is not None:
        query = query.filter(WorkSchedule.line_id == line_id)
    if status:
        query = query.filter(WorkSchedule.status == status)

    total = query.count()
    schedules = (
        db.query(WorkSchedule)
        .options(joinedload(WorkSchedule.line))
        .order_by(WorkSchedule.line_id, WorkSchedule.weekday)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "schedules": [schedule_to_response(s) for s in schedules],
    }


@router.get("/{schedule_id}")
async def get_schedule(
    request: Request, schedule_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    schedule = (
        db.query(WorkSchedule)
        .options(joinedload(WorkSchedule.line))
        .filter(WorkSchedule.id == schedule_id)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule_to_response(schedule)


@router.post("", status_code=201)
async def create_schedule(
    request: Request, body: WorkScheduleCreate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    line = db.query(Line).filter(Line.id == body.line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")

    schedule = WorkSchedule(
        line_id=body.line_id,
        weekday=body.weekday,
        start_time=body.start_time,
        end_time=body.end_time,
        status=getattr(body, 'status', "free"),
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    schedule = db.query(WorkSchedule).options(joinedload(WorkSchedule.line)).filter(WorkSchedule.id == schedule.id).first()
    return schedule_to_response(schedule)


@router.put("/{schedule_id}")
async def update_schedule(
    request: Request, schedule_id: int, body: WorkScheduleUpdate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    schedule = db.query(WorkSchedule).filter(WorkSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    schedule = db.query(WorkSchedule).options(joinedload(WorkSchedule.line)).filter(WorkSchedule.id == schedule.id).first()
    return schedule_to_response(schedule)


@router.patch("/{schedule_id}")
async def patch_schedule(
    request: Request, schedule_id: int, body: WorkScheduleUpdate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    schedule = db.query(WorkSchedule).filter(WorkSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)

    schedule = db.query(WorkSchedule).options(joinedload(WorkSchedule.line)).filter(WorkSchedule.id == schedule.id).first()
    return schedule_to_response(schedule)


@router.delete("/{schedule_id}")
async def delete_schedule(
    request: Request, schedule_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    schedule = db.query(WorkSchedule).filter(WorkSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted successfully"}