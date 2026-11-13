# Beauty Salon Manager

A beauty salon management system with a decoupled architecture (Frontend + Backend), including appointment management, customers, services, and user roles.

---

## 🏗️ Architecture

| Layer | Technology | Default Port |
|---|---|---|
| Backend | FastAPI + Uvicorn | `8000` |
| Frontend | Vue 3 + Vite | `5173` |
| Database | SQLite (`saloon.db`) | — |

---

## 📁 Project Structure

```text
project_v7/
├── backend/
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── static/         # Static assets
│   │   ├── database.py     # Database connection
│   │   └── main.py         # FastAPI entry point
│   ├── requirements.txt
│   └── seedtest.py         # Seed data script
├── frontend/
│   ├── src/
│   │   ├── views/          # Vue pages
│   │   ├── api.js          # Backend communication layer
│   │   ├── auth.js         # Token / auth handling
│   │   ├── router.js       # Routing
│   │   └── App.vue
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── start.py                # Runs frontend + backend together
├── .gitignore
└── README.md
⚙️ Prerequisites
Python 3.10+

Node.js 18+ and npm

Windows (the start.py script uses taskkill; it needs changes for Linux/macOS)

🚀 Installation & Running
1. Clone the project
bash
git clone <repo-url>
cd project_v7
2. Set up the Backend
powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt
3. Set up the Frontend
powershell
cd frontend
npm install
cd ..
4. Run both together
powershell
py start.py
This script:

Starts Vite (frontend) on port 5173,

Runs FastAPI (backend) at http://127.0.0.1:8000,

Cleanly shuts down both on Ctrl+C.

5. Run separately (optional)
Backend:

powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Frontend:

powershell
cd frontend
npm run dev
🔗 Important URLs
Service	URL
Frontend	http://localhost:5173
Backend	http://127.0.0.1:8000
API Docs (Swagger)	http://127.0.0.1:8000/docs
ReDoc	http://127.0.0.1:8000/redoc
🗄️ Database
Uses SQLite; the file is at backend/saloon.db.

To load initial data:

powershell
cd backend
py seedtest.py
Files matching *.db are listed in .gitignore and are not committed.

📝 Development Notes
Add the Landing Page.
Add the initial license.

📄 License
This project was developed for educational and personal use.

---

## Vercel preview deployment (multi-service)

The repository includes a Vercel multi-service configuration:

- `frontend`: Vue 3 + Vite, publicly served at `/`.
- `backend`: FastAPI, publicly reached through `/api` and `/api/*`.
- The frontend sends same-origin requests to `/api`; no backend URL or service binding is required.
- Vue Router history routes fall back to `frontend/index.html`.

Set these Project Environment Variables in Vercel for the backend service (and the relevant deployment environments):

- `SESSION_SECRET`: a long, random secret used to sign session cookies.
- `INITIAL_ADMIN_USERNAME`: the demo administrator's username.
- `INITIAL_ADMIN_PASSWORD`: a strong, private demo password.

The backend creates this initial administrator in the current SQLite database when that username does not exist. Do not use a real password or real customer information in a public demo.

**SQLite limitation on Vercel:** this configuration puts the SQLite file in `/tmp/saloon.db` when running on Vercel so the function can write to its temporary filesystem. This is only a disposable preview/testing workaround, not durable database hosting. Vercel function instances have separate ephemeral filesystems; data may disappear after an instance is recycled and may not be shared across instances. Therefore logins and records are not guaranteed to remain available or consistent. Do not use this setup for production or real salon/customer data. For a reliable live demo with working CRUD, migrate the database to a managed database such as PostgreSQL.
