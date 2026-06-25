# Fixora — Implementation Guide

## Run without Docker (recommended if Docker is not installed)

```powershell
cd "C:\Users\ishini.rathnayake\Desktop\my\University Projects\Fixora"
.\run-local.ps1
```

Requires **Python 3.12+** and **Node.js** only. Uses **SQLite** (no MySQL).

`.\run.ps1` will automatically call `run-local.ps1` if Docker is missing.

---

## Run the full system (Docker)

```powershell
.\run.ps1
```

(Only works after installing [Docker Desktop](https://www.docker.com/products/docker-desktop/).)

Or:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:5173 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

**Login:** `admin@fixora.local` / `admin123`  
**Viewer:** `viewer@fixora.local` / `viewer123`

Users are created automatically when the API starts (`backend/app/startup.py`).

---

## Demo workflow

1. **Logs** → Load sample logs → Run AI analysis pipeline  
2. **Dashboard** → health score, alerts, diagnostics  
3. **Diagnostics** → plain-English root causes  
4. **Ask Fixora** → full diagnostic or SQL-only query  
5. **Enterprise** → Process order → new logs → re-analyze  
6. **Alerts** → Acknowledge (admin)  
7. **Settings** → RBAC permissions  

---

## Run without Docker

**Terminal 1 — MySQL:** use Docker only for DB: `docker compose up -d mysql`

**Terminal 2 — API:**
```powershell
cd backend
pip install -r requirements.txt
$env:MYSQL_HOST="localhost"
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — UI:**
```powershell
cd frontend
npm install
npm run dev
```

---

## Optional: Grok API

Add to `.env`:
```
XAI_API_KEY=your_key_here
```

Without it, the system uses deterministic fallbacks for diagnostics and SQL.

---

## Project structure

```
backend/app/agents/     Monitoring, Analysis, Data Retrieval, Orchestrator
backend/app/services/   Pipeline, LLM, log parser, anomaly ML
frontend/src/pages/     All UI screens (matches Figma wireframes)
database/schema.sql     MySQL schema
design/figma-wireframes/  UI reference + import-ready HTML
```

---

## Tests

```powershell
cd backend
pip install -r requirements.txt
pytest tests/ -v
```
