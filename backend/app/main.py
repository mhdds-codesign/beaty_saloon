from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
import hashlib
from sqlalchemy.orm import Session

from sqlalchemy import text

from app.database import engine, Base, get_db
from app.models import Admin

# Import روترهای ما
from app.api.auth_api import router as auth_router
from app.api.dashboard_api import router as dashboard_router
from app.api.customers_api import router as customers_router
from app.api.lines_api import router as lines_router
from app.api.reservations_api import router as reservations_router
from app.api.workschedules_api import router as workschedules_router

# ایجاد جداول دیتابیس (در صورت عدم وجود)
Base.metadata.create_all(bind=engine)


# ======================== مهاجرت سبک: افزودن ستون‌های نقش به جدول admins ========================
# SQLite با create_all ستون جدید به جدول موجود اضافه نمی‌کند، پس دستی و به‌صورت idempotent اضافه می‌کنیم.
def _ensure_admin_role_columns():
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(admins)"))}
        if "role" not in existing:
            conn.execute(text("ALTER TABLE admins ADD COLUMN role VARCHAR NOT NULL DEFAULT 'admin'"))
        if "customer_id" not in existing:
            conn.execute(text("ALTER TABLE admins ADD COLUMN customer_id INTEGER"))
        conn.commit()


_ensure_admin_role_columns()

app = FastAPI(
    title="Beauty Saloon Management System",
    docs_url=None,  
    redoc_url=None
)

# ======================== Middleware ========================
app.add_middleware(
    SessionMiddleware,
    secret_key="this-is-secret-key-for-saloon"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ======================== Include Routers ========================
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(customers_router)
app.include_router(lines_router)
app.include_router(reservations_router)
app.include_router(workschedules_router)


# ======================== امنیت Swagger (اختیاری) ========================
security = HTTPBasic(auto_error=False)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    pw_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    admin = db.query(Admin).filter(
        Admin.username == credentials.username,
        Admin.password_hash == pw_hash,
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Saloon API")


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    pw_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    admin = db.query(Admin).filter(
        Admin.username == credentials.username,
        Admin.password_hash == pw_hash,
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return app.openapi()


@app.get("/")
async def root():
    return RedirectResponse("/docs")