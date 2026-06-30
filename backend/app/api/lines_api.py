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

# تابع مرتب‌سازی فارسی در پایتون
def persian_sort_key(text):
    """مرتب‌سازی بر اساس الفبای فارسی"""
    persian_alphabet = 'آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
    
    if not text:
        return []
    
    result = []
    for char in text:
        if char in persian_alphabet:
            result.append(persian_alphabet.index(char))
        else:
            result.append(ord(char))
    return result


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
    search: str = Query(""),
    min_price: float = Query(None),
    max_price: float = Query(None),
    per_page: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if not require_auth(request):
        return JSONResponse(status_code=401, content={"message": "Not authenticated"})

    query = db.query(Line)
    
    # جستجو
    if search:
        query = query.filter(
            Line.name_line.ilike(f"%{search}%") | 
            Line.name_service.ilike(f"%{search}%")
        )

    # دریافت همه داده‌ها برای مرتب‌سازی در پایتون
    all_lines = query.all()
    
    # مرتب‌سازی در پایتون با استفاده از persian_sort_key
    order_map = {
        "default": lambda: sorted(all_lines, key=lambda x: x.id),
        "name_line": lambda: sorted(all_lines, key=lambda x: persian_sort_key(x.name_line or '')),
        "name_service": lambda: sorted(all_lines, key=lambda x: persian_sort_key(x.name_service or '')),
        "price": lambda: sorted(all_lines, key=lambda x: x.price or 0),
    }
    
    # اجرای مرتب‌سازی
    sorted_lines = order_map.get(sort, order_map["default"])()
    
    # صفحه‌بندی در پایتون
    total = len(sorted_lines)
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_lines = sorted_lines[start:end]

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (total + per_page - 1) // per_page),
        "lines": [line_to_response(l) for l in paginated_lines],
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