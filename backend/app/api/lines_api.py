from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Line
from app.schemas.line import LineCreate, LineUpdate, LineResponse

router = APIRouter(prefix="/api/lines", tags=["Lines"])


def require_auth(request: Request):
    if not request.session.get("admin_id"):
        return False
    return True


def line_to_response(l: Line) -> LineResponse:
    return LineResponse(
        id=l.id,
        name_line=l.name_line,
        name_service=l.name_service,
        duration_minutes=l.duration_minutes,
        price=l.price,
    )


@router.get("")
async def list_lines(
    request: Request,
    sort: str = Query("default"),
    page: int = Query(1, ge=1),
    q: str = Query(""),
    min_price: float = Query(None),
    max_price: float = Query(None),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    query = db.query(Line)
    
    # جستجو
    if q:
        query = query.filter(
            Line.name_line.ilike(f"%{q}%") | 
            Line.name_service.ilike(f"%{q}%")
        )
    
    # فیلتر قیمت
    if min_price is not None:
        query = query.filter(Line.price >= min_price)
    if max_price is not None:
        query = query.filter(Line.price <= max_price)

    # مرتب‌سازی
    order_map = {
        "name_line": Line.name_line,
        "price": Line.price,
    }
    order_col = order_map.get(sort, Line.id)
    query = query.order_by(order_col)

    total = query.count()
    lines = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "lines": [line_to_response(l) for l in lines],
    }


@router.get("/{line_id}")
async def get_line(
    request: Request, line_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    line = db.query(Line).filter(Line.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")
    
    return line_to_response(line)


@router.post("", status_code=201)
async def create_line(
    request: Request, body: LineCreate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    line = Line(**body.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    
    return line_to_response(line)


@router.put("/{line_id}")
async def update_line(
    request: Request, line_id: int, body: LineCreate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    line = db.query(Line).filter(Line.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")
    
    for key, val in body.model_dump().items():
        setattr(line, key, val)
    
    db.commit()
    db.refresh(line)
    return line_to_response(line)


@router.patch("/{line_id}")
async def patch_line(
    request: Request, line_id: int, body: LineUpdate, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    line = db.query(Line).filter(Line.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")
    
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(line, key, val)
    
    db.commit()
    db.refresh(line)
    return line_to_response(line)


@router.delete("/{line_id}")
async def delete_line(
    request: Request, line_id: int, db: Session = Depends(get_db)
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})
    
    line = db.query(Line).filter(Line.id == line_id).first()
    if not line:
        raise HTTPException(status_code=404, detail="Line not found")
    
    db.delete(line)
    db.commit()
    return {"message": "Line deleted successfully"}