# Fixora — Design Diagrams (Section 4.4)

**Student ID:** 2521838  
**Project:** Multi-Agent AI-Based Automated Administrative System for Enterprise Business Operations  
**Reference:** Contextual Report (CIS013-3), Section 4.4 — Design  

Use these diagrams in your thesis/report. Export via [Mermaid Live](https://mermaid.live), draw.io (Mermaid plugin), or MySQL Workbench (for ER).

---

## Figure A: Entity–Relationship (ER) Diagram

*Covers: user accounts and roles (FR5), log records (FR1), system alerts, agent outputs, operational data, and NL query audit (FR3).*

```mermaid
erDiagram
    ROLES ||--o{ USERS : assigns
    USERS ||--o{ NL_QUERIES : submits
    USERS ||--o{ ALERTS : acknowledges

    LOG_SOURCES ||--o{ LOG_ENTRIES : generates
    LOG_ENTRIES ||--o| ALERTS : triggers

    ALERTS ||--o| DIAGNOSTICS : explained_by

    ROLES {
        tinyint id PK
        varchar name UK
        varchar description
    }

    USERS {
        int id PK
        varchar email UK
        varchar password_hash
        varchar full_name
        tinyint role_id FK
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    LOG_SOURCES {
        smallint id PK
        varchar name UK
        enum source_type
        varchar description
    }

    LOG_ENTRIES {
        bigint id PK
        smallint source_id FK
        timestamp logged_at
        enum level
        text message
        varchar template_id
        text raw_line
        json metadata_json
        boolean is_anomaly
        float anomaly_score
        timestamp created_at
    }

    ALERTS {
        int id PK
        enum severity
        varchar title
        text summary
        enum status
        bigint log_entry_id FK
        timestamp detected_at
        int acknowledged_by FK
        timestamp resolved_at
    }

    DIAGNOSTICS {
        int id PK
        int alert_id FK
        text root_cause
        text explanation
        text remediation
        decimal confidence
        varchar model_version
        timestamp created_at
    }

    AGENT_RUNS {
        bigint id PK
        enum agent_name
        enum trigger_type
        text input_summary
        text output_summary
        enum status
        int duration_ms
        timestamp started_at
        timestamp completed_at
    }

    NL_QUERIES {
        bigint id PK
        int user_id FK
        text natural_language
        text generated_sql
        boolean is_valid_sql
        int result_row_count
        int latency_ms
        text error_message
        timestamp created_at
    }

    HEALTH_METRICS {
        int id PK
        varchar metric_name
        decimal metric_value
        varchar unit
        timestamp recorded_at
    }

    ORDERS {
        int id PK
        varchar order_ref
        varchar customer_name
        enum status
        decimal total_amount
        timestamp created_at
    }

    INVENTORY {
        int id PK
        varchar sku UK
        varchar product_name
        int quantity
        timestamp updated_at
    }
```

**Cardinality notes**

| Relationship | Meaning |
|--------------|---------|
| ROLES → USERS | One role; many users (administrator, viewer) |
| LOG_SOURCES → LOG_ENTRIES | One source (app, API, DB); many log lines |
| LOG_ENTRIES → ALERTS | Optional link when Monitoring Agent raises alert |
| ALERTS → DIAGNOSTICS | Analysis Agent may produce one diagnostic per alert |
| USERS → NL_QUERIES | Audit trail for Data Retrieval Agent (FR3) |
| AGENT_RUNS | Standalone audit of each agent execution |

---

## Figure B: Domain Class Diagram (UML)

*Logical object model corresponding to the ER schema and agent outputs.*

```mermaid
classDiagram
    direction TB

    class Role {
        +int id
        +string name
        +string description
    }

    class User {
        +int id
        +string email
        +string passwordHash
        +string fullName
        +bool isActive
        +authenticate()
    }

    class LogSource {
        +int id
        +string name
        +string sourceType
    }

    class LogEntry {
        +long id
        +DateTime loggedAt
        +string level
        +string message
        +string templateId
        +bool isAnomaly
        +float anomalyScore
    }

    class Alert {
        +int id
        +string severity
        +string title
        +string summary
        +string status
        +DateTime detectedAt
        +acknowledge(userId)
    }

    class Diagnostic {
        +int id
        +string rootCause
        +string explanation
        +string remediation
        +float confidence
        +string modelVersion
    }

    class AgentRun {
        +long id
        +string agentName
        +string triggerType
        +string status
        +int durationMs
    }

    class NLQuery {
        +long id
        +string naturalLanguage
        +string generatedSql
        +bool isValidSql
        +int latencyMs
    }

    class HealthMetric {
        +int id
        +string metricName
        +float metricValue
    }

    class Order {
        +int id
        +string orderRef
        +string status
        +decimal totalAmount
    }

  class InventoryItem {
        +int id
        +string sku
        +int quantity
    }

    class MonitoringAgent {
        +parseLogs()
        +detectAnomalies()
        +createAlerts()
    }

    class AnalysisAgent {
        +generateDiagnostic(context)
    }

    class DataRetrievalAgent {
        +translateToSql(question)
        +validateSql()
        +executeQuery()
    }

    class AgentOrchestrator {
        +runMonitoringPipeline()
        +runNlQuery()
        +runFullDiagnosticQuery()
    }

    Role "1" --> "*" User : has
    User "1" --> "*" NLQuery : submits
    User "1" --> "*" Alert : acknowledges
    LogSource "1" --> "*" LogEntry : contains
    LogEntry "0..1" --> "0..*" Alert : mayTrigger
    Alert "0..1" --> "0..1" Diagnostic : has
    AgentOrchestrator --> MonitoringAgent : coordinates
    AgentOrchestrator --> AnalysisAgent : coordinates
    AgentOrchestrator --> DataRetrievalAgent : coordinates
    MonitoringAgent ..> LogEntry : updates
    MonitoringAgent ..> Alert : creates
    AnalysisAgent ..> Diagnostic : creates
    DataRetrievalAgent ..> NLQuery : logs
```

---

## Figure C: Sequence Diagram 1 — Natural Language Diagnostic Query (Section 4.3 use case)

*Administrator asks: “What caused the database slowdown in the last hour?” — full agent pipeline (FR1–FR3).*

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant UI as React Dashboard
    participant API as FastAPI API
    participant Orch as Agent Orchestrator
    participant Mon as Monitoring Agent
    participant Ana as Analysis Agent
    participant DRA as Data Retrieval Agent
    participant Grok as Grok xAI API
    participant DB as MySQL

    Admin->>UI: Enter NL question + view alerts
    UI->>API: POST /api/v1/agents/analyze {question, limit}
    API->>DB: SELECT log_entries (recent window)
    DB-->>API: Log rows

    API->>Orch: run_full_diagnostic_query(question, logs)

    Orch->>Mon: run(log_window)
    Mon->>Mon: Drain3 parse + Isolation Forest
    Mon-->>Orch: anomalies, alerts

    alt anomalies detected
        Orch->>Ana: run(context)
        Ana->>Grok: prompt(anomalies, schema)
        Grok-->>Ana: JSON root_cause, explanation, remediation
        Ana-->>Orch: diagnostic (plain English)
    end

    Orch->>DRA: run(nl_query)
    DRA->>Grok: NL to SQL(schema, question)
    Grok-->>DRA: SELECT statement
    DRA->>DRA: validate SQL (whitelist, SELECT-only)
    DRA->>DB: execute safe query
    DB-->>DRA: result rows
    DRA-->>Orch: SQL + rows

    Orch-->>API: pipeline + nl_query results
    API->>DB: INSERT alerts, diagnostics, agent_runs, nl_queries
    API-->>UI: JSON response
    UI-->>Admin: Diagnosis + query table (< 5s NFR1)
```

---

## Figure D: Sequence Diagram 2 — Automated Log Monitoring and Alert Workflow (FR1)

*Log ingestion → anomaly detection → alert → optional diagnostic → dashboard.*

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant UI as React Dashboard
    participant API as FastAPI API
    participant Parser as Drain3 Log Parser
    participant Orch as Agent Orchestrator
    participant Mon as Monitoring Agent
    participant Ana as Analysis Agent
    participant Grok as Grok xAI API
    participant DB as MySQL

    Admin->>UI: Load sample logs / upload file
    UI->>API: POST /api/v1/logs/ingest/sample
    loop each log line
        API->>Parser: parse_line(raw)
        Parser-->>API: template_id, level, message
        API->>DB: INSERT log_entries
    end
    API-->>UI: entries_stored

    Admin->>UI: Run AI analysis pipeline
    UI->>API: POST /api/v1/agents/analyze
    API->>DB: SELECT log_entries
    DB-->>API: log window

    API->>Orch: run_monitoring_pipeline(logs)
    Orch->>Mon: run(context)
    Mon->>Mon: feature matrix + Isolation Forest
    Mon-->>Orch: anomaly_count, alerts[]

    alt anomaly_count > 0
        Orch->>Ana: run(context)
        Ana->>Grok: structured diagnostic prompt
        Grok-->>Ana: root cause + remediation
        Ana-->>Orch: diagnostic
    end

    Orch-->>API: agent_runs + context
    API->>DB: UPDATE log_entries.is_anomaly
    API->>DB: INSERT alerts, diagnostics, agent_runs
    API->>DB: INSERT health_metrics
    API-->>UI: pipeline result

    UI->>API: GET /api/v1/dashboard/summary
    API->>DB: SELECT alerts, diagnostics, metrics
    DB-->>API: aggregated data
    API-->>UI: health score, recent alerts
    UI-->>Admin: Unified dashboard (FR4)
```

---

## Figure E: DFD Level 0 (Context diagram)

*Required in contextual report Section 4.4 — single process view.*

```mermaid
flowchart LR
    subgraph external [External entities]
        BU[Business User]
        IT[IT Administrator]
        Logs[(Log files / Enterprise app)]
    end

    subgraph system [Fixora System]
        FIXORA[0 Fixora Multi-Agent Admin System]
    end

    Grok[Grok xAI API]

    Logs --> FIXORA
    BU --> FIXORA
    IT --> FIXORA
    FIXORA --> Grok
    Grok --> FIXORA
    FIXORA --> BU
    FIXORA --> IT
```

---

## Figure F: DFD Level 1

```mermaid
flowchart TB
    Logs[Log sources] --> P1[1.0 Ingest and parse logs]
    P1 --> D1[(D1 Log store)]
    D1 --> P2[2.0 Monitor and detect anomalies]
    P2 --> D2[(D2 Alerts)]
    P2 --> P3[3.0 Analyse and diagnose]
    P3 --> Grok[Grok API]
    Grok --> P3
    P3 --> D3[(D3 Diagnostics)]
    User[User] --> P4[4.0 NL query and retrieve data]
    P4 --> Grok
    P4 --> D4[(D4 Operational DB)]
    D1 --> P2
    D2 --> P5[5.0 Present dashboard]
    D3 --> P5
    D4 --> P5
    P5 --> User
```

---

## How to cite in your report

| Figure | Suggested caption |
|--------|-------------------|
| A | *Entity–Relationship diagram of the Fixora MySQL database schema.* |
| B | *UML domain class diagram showing core entities and multi-agent components.* |
| C | *Sequence diagram: natural language diagnostic query through the multi-agent pipeline (FR1–FR3).* |
| D | *Sequence diagram: automated log monitoring, alerting, and dashboard update (FR1, FR4).* |
| E–F | *Data flow diagrams Level 0 and Level 1 for the Fixora system.* |

**Source:** Researcher's own design based on implemented schema (`database/schema.sql`) and Contextual Report Section 4.3–4.4.

---

## MySQL Workbench

1. **Database → Reverse Engineer** from a running Fixora MySQL instance, or  
2. **File → Import → Reverse Engineer SQL Create Script** → select `database/schema.sql`  
3. Export as PNG/PDF for the thesis (**Figure: ER Diagram**).
