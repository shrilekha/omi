-- omi-benchmarks — Industry Benchmark Reference Data
-- MySQL schema for production deployment
-- SQLite equivalent is auto-created by backend/db.py on first run
--
-- Separate database from both OMI and omi-deepdive. This holds anonymized,
-- aggregate peer-comparison figures (not any single client's raw response
-- data), read by both of those apps' backends over the /api/benchmarks
-- endpoint — never called directly from either app's browser-facing pages.
--
-- Entered ONCE, app-agnostically: `metric` is a canonical capability area
-- (see backend/constants.py METRICS), not tied to either app's own domain/
-- dimension taxonomy. Each consuming app maps its own ids onto these when
-- it reads — see OMI_METRIC_TO_CANONICAL / DEEPDIVE_METRIC_TO_CANONICAL in
-- each app's own backend/app.py.

CREATE TABLE IF NOT EXISTS benchmarks (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    -- capability-area id, or 'overall' — see constants.py METRICS
    metric          VARCHAR(30)  NOT NULL,
    -- industry archetype id, or 'all' for a cross-sector rollup
    sector          VARCHAR(30)  NOT NULL,
    -- country/region, or 'all'
    geo             VARCHAR(30)  NOT NULL,
    -- revenue band id, or 'all'
    revenue_band    VARCHAR(20)  NOT NULL,

    benchmark_value DECIMAL(5,2) NOT NULL,
    sample_size     INT,
    source          VARCHAR(255),
    effective_date  DATE,
    created_by      VARCHAR(255),

    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uniq_peer_group (metric, sector, geo, revenue_band),
    INDEX idx_metric (metric),
    INDEX idx_sector (sector)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
