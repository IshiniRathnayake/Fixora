# Fixora

**Multi-Agent AI-Based Automated Administrative System for Enterprise Business Operations**

BSc (Hons) Computer Science — CIS013-3 Research Methodologies and Emerging Technologies.

## Overview

Fixora is a research prototype that combines:

- **Monitoring Agent** — real-time log ingestion, Drain3 parsing, Isolation Forest anomaly detection (FR1)
- **Analysis & Diagnostic Agent** — plain-English root-cause explanations via Grok/xAI (FR2)
- **Data Retrieval Agent** — natural language to SQL with schema validation (FR3)
- **React dashboard** — unified health view, alerts, agent activity (FR4)
- **RBAC** — administrator and viewer roles (FR5)

## Quick start

### Prerequisites

- Docker Desktop (recommended), or Python 3.12+, Node 20+, MySQL 8

### 1. Run (Windows)

```powershell
.\run.ps1
```

Creates `.env` if missing and starts MySQL + API + UI. Demo users are seeded on API startup.

### 2. Or manually

```bash
cp .env.example .env
docker compose up --build
```

- UI: http://localhost:5173  
- API: http://localhost:8000/docs  

See **[IMPLEMENTATION.md](IMPLEMENTATION.md)** for full guide.

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@fixora.local | admin123 |
| Viewer | viewer@fixora.local | viewer123 |

### 4. Demo workflow

1. Sign in as **admin@fixora.local** / **admin123**
2. **Logs** → *Load sample logs* → *Run AI analysis pipeline*
3. **Diagnostics** → view plain-English root cause + remediation
4. **Ask Fixora** → *What caused the database slowdown in the last hour?* (full diagnostic mode)
5. **Enterprise** → process an order to emit new logs, then re-analyze

### Kaggle / CSV log import

```bash
python scripts/ingest_csv_logs.py path/to/logs.csv --limit 10000
cd backend && python -m pytest tests/ -v
```

## Local development (without Docker)

```bash
# MySQL: run database/schema.sql
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload

cd frontend && npm install && npm run dev
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | OAuth2 password login |
| GET | `/api/v1/dashboard/summary` | Unified health dashboard |
| POST | `/api/v1/agents/pipeline` | Monitoring → diagnostic pipeline |
| POST | `/api/v1/agents/query` | Natural language data query |
| GET | `/api/v1/logs/` | List ingested logs |
| POST | `/api/v1/logs/ingest/sample` | Load bundled sample logs |

## Testing

```bash
cd backend
pytest tests/ -v
```

## Project structure

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for diagrams and agent design.

## Research alignment

Requirements map to survey evidence (Table 3 in contextual report):

- FR1–FR5 implemented in `backend/app/agents/` and `frontend/src/pages/`
- Evaluation metrics: precision/recall (anomaly), NLP query success (30 cases), SUS usability (UAT)

## License

Academic research prototype — University of Bedfordshire.
