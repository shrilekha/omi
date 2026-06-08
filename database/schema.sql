-- OMI — Observability Maturity Index
-- MySQL schema for production deployment
-- SQLite equivalent is auto-created by backend/db.py on first run

CREATE TABLE IF NOT EXISTS submissions (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    session_id       VARCHAR(36)  NOT NULL UNIQUE,
    submitted_at     DATETIME     DEFAULT CURRENT_TIMESTAMP,
    email            VARCHAR(255) NOT NULL,
    first_name       VARCHAR(100),
    last_name        VARCHAR(100),
    role             VARCHAR(100),
    sector           VARCHAR(100),
    country          VARCHAR(100),
    sector_archetype VARCHAR(50),
    question_variant VARCHAR(50),

    -- 25 answer scores (1–5 per question)
    txn1   TINYINT UNSIGNED, txn2  TINYINT UNSIGNED, txn3  TINYINT UNSIGNED,
    txn4   TINYINT UNSIGNED, txn5  TINYINT UNSIGNED,
    app1   TINYINT UNSIGNED, app2  TINYINT UNSIGNED, app3  TINYINT UNSIGNED,
    app4   TINYINT UNSIGNED, app5  TINYINT UNSIGNED,
    infra1 TINYINT UNSIGNED, infra2 TINYINT UNSIGNED, infra3 TINYINT UNSIGNED,
    infra4 TINYINT UNSIGNED, infra5 TINYINT UNSIGNED,
    log1   TINYINT UNSIGNED, log2  TINYINT UNSIGNED, log3  TINYINT UNSIGNED,
    log4   TINYINT UNSIGNED, log5  TINYINT UNSIGNED,
    comp1  TINYINT UNSIGNED, comp2 TINYINT UNSIGNED, comp3 TINYINT UNSIGNED,
    comp4  TINYINT UNSIGNED, comp5 TINYINT UNSIGNED,

    -- Computed scores (0–100 per domain, 0–100 overall)
    txn_score    DECIMAL(5,2),
    app_score    DECIMAL(5,2),
    infra_score  DECIMAL(5,2),
    log_score    DECIMAL(5,2),
    comp_score   DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    maturity_band VARCHAR(20),

    INDEX idx_email (email),
    INDEX idx_archetype (sector_archetype),
    INDEX idx_country (country),
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
