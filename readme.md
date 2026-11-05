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