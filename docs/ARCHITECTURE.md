# Fixora — System Architecture

Aligned with CIS013-3 contextual report (Section 4.3–4.4).

## Three-layer model

```mermaid
flowchart TB
    subgraph interaction [Interaction Layer]
        UI[React Dashboard FR4]
        DRA[Data Retrieval Agent FR3]
    end

    subgraph reasoning [Reasoning Layer]
        ADA[Analysis and Diagnostic Agent FR2]
        LLM[Grok xAI API]
    end

    subgraph perception [Perception Layer]
        MA[Monitoring Agent FR1]
        DRAIN[Drain3 Log Parser]
        IF[Isolation Forest]
    end

    subgraph orchestration [Orchestration]
        LC[Agent Orchestrator LangChain-style]
    end

    UI --> API[FastAPI REST]
    API --> LC
    LC --> MA
    LC --> ADA
    LC --> DRA
    MA --> DRAIN
    MA --> IF
    ADA --> LLM
    DRA --> LLM
    MA --> DB[(MySQL)]
    ADA --> DB
    DRA --> DB
```

## Agent responsibilities

| Agent | Layer | Requirements | Techniques |
|-------|-------|--------------|------------|
| Monitoring | Perception | FR1 | Drain3 templates, Isolation Forest, threshold alerts |
| Analysis/Diagnostic | Reasoning | FR2 | Anomaly context + Grok → plain-English root cause |
| Data Retrieval | Interaction | FR3 | Schema-aware NL→SQL, whitelist validation |
| Orchestrator | Coordination | NFR3 | Pipeline: Monitoring → Analysis; standalone NL queries |

## Security (FR5)

- JWT authentication
- Roles: `administrator` (full), `viewer` (read-only)
- SQL sandbox: SELECT-only, table whitelist, no DDL/DML

## Evaluation hooks (Section 4.7)

- `backend/tests/test_anomaly.py` — detection unit tests
- `backend/tests/test_sql_validation.py` — NL query safety
- Baseline: `AnomalyDetectionService.rule_based_baseline()` for comparison with Isolation Forest

## Repository layout

```
Fixora/
├── backend/app/agents/     # Multi-agent implementations
├── backend/app/services/   # LLM, parsing, ML
├── frontend/src/pages/     # Dashboard, Alerts, Logs, Query
├── database/schema.sql     # ER model
└── docs/ARCHITECTURE.md
```
