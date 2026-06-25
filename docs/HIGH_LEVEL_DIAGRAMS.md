# Fixora — High-Level Diagrams

**Student ID:** 2521838 | **Section 4.4 / Figure 15 style**  
Use [Mermaid Live](https://mermaid.live) to export PNG/SVG for Word or PowerPoint.

---

## Figure 1 — System context (highest level)

*Who interacts with Fixora and what sits outside the system.*

```mermaid
flowchart TB
    subgraph users [Users]
        BU[Business User\nnon-technical]
        IT[IT Administrator]
    end

    subgraph fixora [Fixora System]
        SYS[Multi-Agent AI\nAdministrative System]
    end

    subgraph external [External]
        APP[Enterprise Application\n+ Database]
        LOGS[Server / Application Logs]
        AI[Grok xAI API]
    end

    BU --> SYS
    IT --> SYS
    LOGS --> SYS
    APP --> SYS
    SYS --> AI
    SYS --> BU
    SYS --> IT
```

---

## Figure 2 — High-level system architecture

*Main building blocks (matches Contextual Report Figure 15).*

```mermaid
flowchart TB
    subgraph presentation [Presentation Layer]
        UI[React.js Dashboard\nFR4 · RBAC FR5]
    end

    subgraph api [Application Layer]
        REST[FastAPI REST API]
    end

    subgraph agents [Multi-Agent Layer — LangChain-style Orchestration]
        ORCH[Agent Orchestrator]
        MA[Monitoring Agent\nFR1]
        AA[Analysis & Diagnostic Agent\nFR2]
        DA[Data Retrieval Agent\nFR3]
    end

    subgraph intelligence [AI / Analytics]
        ML[Drain3 + Isolation Forest\n+ scikit-learn]
        LLM[Grok xAI\nNLP & diagnostics]
    end

    subgraph data [Data Layer]
        DB[(MySQL\nlogs · alerts · diagnostics\nenterprise data)]
    end

    UI <-->|HTTPS / JWT| REST
    REST --> ORCH
    ORCH --> MA
    ORCH --> AA
    ORCH --> DA
    MA --> ML
    AA --> LLM
    DA --> LLM
    MA --> DB
    AA --> DB
    DA --> DB
    REST --> DB
```

---

## Figure 3 — Three-layer conceptual framework (Section 4.3)

*Perception → Reasoning → Interaction.*

```mermaid
flowchart LR
    subgraph L1 [Perception Layer]
        P1[Log ingestion\nAnomaly detection\nAlerts]
    end

    subgraph L2 [Reasoning Layer]
        P2[Root-cause analysis\nPlain-English diagnosis\nRemediation hints]
    end

    subgraph L3 [Interaction Layer]
        P3[Natural language queries\nUnified dashboard]
    end

    P1 -->|anomaly signals| P2
    P2 -->|insights| P3
    P3 -->|user questions| P2
```

---

## Figure 4 — High-level multi-agent collaboration

*How agents work together (no implementation detail).*

```mermaid
flowchart LR
    LOGS[Log stream] --> MA[Monitoring\nAgent]
    MA -->|alert| AA[Analysis\nAgent]
    AA -->|diagnosis| DASH[Dashboard]
    USER[User question] --> DA[Data Retrieval\nAgent]
    DA -->|SQL results| DASH
    MA -.->|context| AA
    ORCH[Orchestrator] -.-> MA
    ORCH -.-> AA
    ORCH -.-> DA
```

---

## Figure 5 — High-level data flow (DFD Level 0)

```mermaid
flowchart LR
    E1[Enterprise logs\n& operations] --> S[Fixora]
    E2[Administrators\n& business users] <--> S
    E3[Cloud LLM\nGrok] <--> S
    S --> O1[Alerts &\nexplanations]
    S --> O2[Query answers\n& health view]
```

---

## Figure 6 — High-level deployment view

```mermaid
flowchart TB
    Browser[Web browser] --> FE[React frontend\n:5173]
    FE --> BE[Python FastAPI\n:8000]
    BE --> MY[(MySQL\n:3306)]
    BE --> XAI[Grok API\nx.ai]
```

---

## Suggested figure captions (for thesis)

| Figure | Caption |
|--------|---------|
| 1 | High-level system context of Fixora showing users, enterprise data sources, and external AI services. |
| 2 | High-level system architecture of the proposed multi-agent AI administrative system. |
| 3 | Three-layer conceptual framework: perception, reasoning, and interaction. |
| 4 | High-level collaboration between Monitoring, Analysis, and Data Retrieval agents. |
| 5 | Context-level data flow diagram (DFD Level 0). |
| 6 | High-level deployment architecture using Docker (frontend, backend, database). |

**Source:** Researcher's own work, Fixora project (2521838), 2026.
