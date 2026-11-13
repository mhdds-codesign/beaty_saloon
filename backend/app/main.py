import os
from pathlib import Path
import hashlib
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, Base, get_db, SessionLocal
from app.models import Admin

# Import routers
from app.api.auth_api import router as auth_router
from app.api.dashboard_api import router as dashboard_router
from app.api.customers_api import router as customers_router
from app.api.lines_api import router as lines_router
from app.api.reservations_api import router as reservations_router
from app.api.workschedules_api import router as workschedules_router

# Create database tables if they do not exist.
Base.metadata.create_all(bind=engine)


# Lightweight, idempotent migration for the admin role columns.
def _ensure_admin_role_columns():
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(admins)"))}
        if "role" not in existing:
            conn.execute(
                text("ALTER TABLE admins ADD COLUMN role VARCHAR NOT NULL DEFAULT 'admin'")
            )
        if "customer_id" not in existing:
            conn.execute(text("ALTER TABLE admins ADD COLUMN customer_id INTEGER"))
        conn.commit()


_ensure_admin_role_columns()


def _ensure_initial_admin():
    """Create the demo admin from environment variables if the current DB is empty."""
    username = os.getenv("INITIAL_ADMIN_USERNAME")
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    if not username or not password:
        return

    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            return
        admin = Admin(
            username=username,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            created_at=datetime.utcnow().isoformat(),
            role="admin",
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()


_ensure_initial_admin()

IS_VERCEL = os.getenv("VERCEL") == "1"
SESSION_SECRET = os.getenv("SESSION_SECRET")

if IS_VERCEL and not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET must be set in Vercel Project Environment Variables."
    )

app = FastAPI(
    title="Beauty Saloon Management System",
    docs_url=None,
    redoc_url=None,
)

# Signed session cookie. On Vercel, require a secret supplied via environment
# variables and mark the cookie Secure because deployments use HTTPS.
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET or "local-development-only-change-this-secret",
    https_only=IS_VERCEL,
    same_site="lax",
)

# Vercel routes the frontend and /api to the same origin, so production API
# requests do not require CORS. These origins keep local Vite development working.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir), check_dir=False), name="static")

# Register API routers. Each router already uses the /api prefix.
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(customers_router)
app.include_router(lines_router)
app.include_router(reservations_router)
app.include_router(workschedules_router)


# Swagger UI is intentionally protected with HTTP Basic authentication.
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
