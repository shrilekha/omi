-- omi-deepdive — Per-App E2E Observability Assessment
-- MySQL schema for production deployment
-- SQLite equivalent is auto-created by backend/db.py on first run
--
-- IMPORTANT: this is a separate database from OMI's own production database
-- (omi_db). This tool holds real client tool-stack and capability-gap data
-- across multiple accounts and must not share infrastructure or credentials
-- with the public-facing OMI survey app.

CREATE TABLE IF NOT EXISTS organizations (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(255) NOT NULL,
    report_token  VARCHAR(64)  NOT NULL UNIQUE,
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS apps (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    organization_id  INT NOT NULL,
    name             VARCHAR(255) NOT NULL,
    owner_name       VARCHAR(255),
    owner_email      VARCHAR(255),
    criticality      VARCHAR(50),
    access_token     VARCHAR(64) NOT NULL UNIQUE,
    created_at       DATETIME    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    INDEX idx_org (organization_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS submissions (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    app_id                 INT NOT NULL,
    session_id             VARCHAR(36) NOT NULL UNIQUE,
    respondent_name        VARCHAR(255),
    respondent_email       VARCHAR(255),
    respondent_role        VARCHAR(255),
    owner_contact          TEXT,
    biggest_blocker        TEXT,

    -- {question_id: score 1-5}
    answers_json           TEXT NOT NULL,
    -- {dimension_id: free-text tool/vendor answer}
    tools_json              TEXT NOT NULL,
    -- {dimension_id: score 0-100, or null if marked not-applicable}
    dimension_scores_json  TEXT NOT NULL,
    -- [dimension_id, ...] dimensions explicitly marked not-applicable (disambiguates
    -- "marked N/A" from "left blank" when dimension_scores_json has a null)
    na_dims_json           TEXT NOT NULL DEFAULT ('[]'),

    overall_score          DECIMAL(5,2),
    maturity_band          VARCHAR(20),
    submitted_at           DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (app_id) REFERENCES apps(id),
    INDEX idx_app (app_id),
    INDEX idx_submitted_at (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Internal RBAC. Only meaningful once Google OAuth admin login is enabled
-- (see .env.example) -- a verified Google identity with no active row here,
-- and not covered by INITIAL_ADMIN_EMAILS at bootstrap, cannot reach any
-- /admin or /dashboard route. Password-mode (ADMIN_KEY) login has no concept
-- of per-user roles; it remains all-or-nothing admin access, as before.
-- This is authorization, distinct from Google OAuth's identity and from the
-- per-app access_token above, which is external respondent access requiring
-- no login and no role at all.
CREATE TABLE IF NOT EXISTS admin_users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    -- admin | assessment_manager | reviewer | executive
    role        VARCHAR(30) NOT NULL,
    is_active   TINYINT(1) NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
