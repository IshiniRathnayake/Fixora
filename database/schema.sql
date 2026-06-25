-- Fixora — Multi-Agent AI Administrative System
-- Entity model aligned with contextual report (Section 4.4)

CREATE DATABASE IF NOT EXISTS fixora CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fixora;

-- RBAC (FR5)
CREATE TABLE roles (
    id          TINYINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(32) NOT NULL UNIQUE,
    description VARCHAR(255)
);

INSERT INTO roles (id, name, description) VALUES
    (1, 'administrator', 'Full access: agents, alerts, users, configuration'),
    (2, 'viewer', 'Read-only: dashboard, alerts, diagnostics');

CREATE TABLE users (
    id            INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(128) NOT NULL,
    role_id       TINYINT UNSIGNED NOT NULL DEFAULT 2,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Enterprise operational data (sample / simulated ERP tables)
CREATE TABLE orders (
    id           INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    order_ref    VARCHAR(64) NOT NULL,
    customer_name VARCHAR(128),
    status       ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    total_amount DECIMAL(12, 2),
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    id           INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    sku          VARCHAR(64) NOT NULL UNIQUE,
    product_name VARCHAR(128) NOT NULL,
    quantity     INT NOT NULL DEFAULT 0,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Log ingestion & monitoring (FR1)
CREATE TABLE log_sources (
    id          SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(64) NOT NULL UNIQUE,
    source_type ENUM('application', 'database', 'api', 'system') NOT NULL,
    description VARCHAR(255)
);

INSERT INTO log_sources (name, source_type, description) VALUES
    ('mysql', 'database', 'MySQL slow query and error logs'),
    ('api', 'api', 'FastAPI application logs'),
    ('app', 'application', 'Simulated enterprise application logs');

CREATE TABLE log_entries (
    id            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    source_id     SMALLINT UNSIGNED NOT NULL,
    logged_at     TIMESTAMP(3) NOT NULL,
    level         ENUM('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL') NOT NULL DEFAULT 'INFO',
    message       TEXT NOT NULL,
    template_id   VARCHAR(64),
    raw_line      TEXT,
    metadata_json JSON,
    is_anomaly    BOOLEAN DEFAULT FALSE,
    anomaly_score FLOAT,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_logged_at (logged_at),
    INDEX idx_level (level),
    INDEX idx_anomaly (is_anomaly),
    FULLTEXT INDEX ft_message (message),
    FOREIGN KEY (source_id) REFERENCES log_sources(id)
);

-- Alerts raised by Monitoring Agent
CREATE TABLE alerts (
    id              INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    severity        ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    title           VARCHAR(255) NOT NULL,
    summary         TEXT NOT NULL,
    status          ENUM('open', 'acknowledged', 'resolved') NOT NULL DEFAULT 'open',
    log_entry_id    BIGINT UNSIGNED,
    detected_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_by INT UNSIGNED,
    resolved_at     TIMESTAMP NULL,
    FOREIGN KEY (log_entry_id) REFERENCES log_entries(id),
    FOREIGN KEY (acknowledged_by) REFERENCES users(id)
);

-- Agent activity & diagnostics (FR2)
CREATE TABLE agent_runs (
    id            BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    agent_name    ENUM('monitoring', 'analysis', 'data_retrieval', 'orchestrator') NOT NULL,
    trigger_type  ENUM('scheduled', 'alert', 'user_query', 'pipeline') NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    status        ENUM('running', 'completed', 'failed') NOT NULL DEFAULT 'running',
    duration_ms   INT UNSIGNED,
    started_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at  TIMESTAMP NULL,
    INDEX idx_agent_started (agent_name, started_at)
);

CREATE TABLE diagnostics (
    id              INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    alert_id        INT UNSIGNED,
    root_cause      TEXT NOT NULL,
    explanation     TEXT NOT NULL,
    remediation     TEXT,
    confidence      DECIMAL(4, 3),
    model_version   VARCHAR(64),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE SET NULL
);

-- NLP query audit (FR3)
CREATE TABLE nl_queries (
    id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id         INT UNSIGNED NOT NULL,
    natural_language TEXT NOT NULL,
    generated_sql   TEXT,
    is_valid_sql    BOOLEAN DEFAULT FALSE,
    result_row_count INT UNSIGNED,
    latency_ms      INT UNSIGNED,
    error_message   TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_created (user_id, created_at)
);

-- System health snapshots for dashboard (FR4)
CREATE TABLE health_metrics (
    id           INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    metric_name  VARCHAR(64) NOT NULL,
    metric_value DECIMAL(12, 4) NOT NULL,
    unit         VARCHAR(16),
    recorded_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_time (metric_name, recorded_at)
);

-- Administrator: run scripts/seed_admin.py after schema load (password: admin123)

INSERT INTO orders (order_ref, customer_name, status, total_amount) VALUES
    ('ORD-1001', 'Acme Corp', 'completed', 1250.00),
    ('ORD-1002', 'Beta Ltd', 'processing', 890.50),
    ('ORD-1003', 'Gamma Inc', 'failed', 320.00);

INSERT INTO inventory (sku, product_name, quantity) VALUES
    ('SKU-A01', 'Widget Alpha', 150),
    ('SKU-B02', 'Component Beta', 42),
    ('SKU-C03', 'Module Gamma', 0);
