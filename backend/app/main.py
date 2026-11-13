import os
import sys
import hashlib
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
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

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # backend/app
BACKEND_DIR = os.path.dirname(BASE_DIR)                    # backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)                # root
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Locate frontend dist
_candidates = [
    os.path.join(PROJECT_ROOT, "frontend", "dist"),
    os.path.join(BACKEND_DIR, "dist"),
    os.path.join(os.getcwd(), "frontend", "dist"),
    os.path.join(os.getcwd(), "dist"),
]
FRONTEND_DIST = next((p for p in _candidates if os.path.isdir(p)), None)

# Create tables
Base.metadata.create_all(bind=engine)


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


# ======================== Startup Event (Auto-seed if empty) ========================
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        if db.query(Admin).count() == 0:
            if BACKEND_DIR not in sys.path:
                sys.path.insert(0, BACKEND_DIR)
            try:
                from seedtest import seed_database
                seed_database()
            except Exception as e:
                print(f"Auto-seed exception: {e}")
    finally:
        db.close()


# ======================== Middleware ========================
app.add_middleware(
    SessionMiddleware,
    secret_key="this-is-secret-key-for-saloon"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================== Static & Frontend Mounting ========================
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if FRONTEND_DIST:
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# ======================== Include Routers ========================
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(customers_router)
app.include_router(lines_router)
app.include_router(reservations_router)
app.include_router(workschedules_router)

# ======================== Swagger Docs (Basic Auth) ========================
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


# ======================== SPA & Root Serving ========================
@app.get("/", include_in_schema=False)
async def root():
    if FRONTEND_DIST:
        index_html = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.isfile(index_html):
            return FileResponse(index_html)
    return RedirectResponse("/docs")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if full_path.startswith(("api", "docs", "openapi.json", "static")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    if FRONTEND_DIST:
        requested_file = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(requested_file):
            return FileResponse(requested_file)
        index_html = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.isfile(index_html):
            return FileResponse(index_html)

    return RedirectResponse("/docs")
