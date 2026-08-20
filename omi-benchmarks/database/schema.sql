-- omi-benchmarks — Industry Benchmark Reference Data
-- MySQL schema for production deployment
-- SQLite equivalent is auto-created by backend/db.py on first run
--
-- Separate database from both OMI and omi-deepdive. This holds anonymized,
-- aggregate peer-comparison figures (not any single client's raw response
-- data), read by both of those apps' backends over the /api/benchmarks
-- endpoint — never called directly from either app's browser-facing pages.

CREATE TABLE IF NOT EXISTS benchmarks (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    -- 'omi' | 'deepdive' — the two apps' domain/dimension taxonomies differ,
    -- so a benchmark row belongs to exactly one of them.
    tool           VARCHAR(20)  NOT NULL,
    -- domain/dimension id for that tool, or 'overall'
    metric         VARCHAR(30)  NOT NULL,
    -- industry archetype id, or 'all' for a cross-sector rollup
    sector         VARCHAR(30)  NOT NULL,
    -- country/region, or 'all'
    geo            VARCHAR(30)  NOT NULL,
    -- revenue band id, or 'all'
    revenue_band   VARCHAR(20)  NOT NULL,

    median_score   DECIMAL(5,2) NOT NULL,
    sample_size    INT,
    source         VARCHAR(255),
    effective_date DATE,
    created_by     VARCHAR(255),

    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_peer_group (tool, metric, sector, geo, revenue_band),
    INDEX idx_tool_sector (tool, sector),
    INDEX idx_tool_metric (tool, metric)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
