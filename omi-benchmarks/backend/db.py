import os
import sqlite3

from constants import ALL_SECTORS, ALL_GEOS, ALL_REVENUE_BANDS, METRICS

ENV = os.getenv('ENV', 'development')

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

_CREATE_SQLITE = """
CREATE TABLE IF NOT EXISTS benchmarks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    metric          TEXT NOT NULL,
    sector          TEXT NOT NULL,
    geo             TEXT NOT NULL,
    revenue_band    TEXT NOT NULL,
    benchmark_value REAL NOT NULL,
    sample_size     INTEGER,
    source          TEXT,
    effective_date  TEXT,
    created_by      TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric, sector, geo, revenue_band)
);
"""


def _get_conn():
    if ENV == 'production':
        import pymysql
        return pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            db=os.getenv('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
    else:
        db_path = os.path.join(_PROJECT_ROOT, os.getenv('SQLITE_PATH', 'local_dev.db'))
        conn = sqlite3.connect(os.path.abspath(db_path))
        conn.row_factory = sqlite3.Row
        return conn


def _placeholder():
    return '%s' if ENV == 'production' else '?'


def init_db():
    if ENV != 'production':
        conn = _get_conn()
        # One-time migration from the old per-tool schema (tool/median_score
        # columns) to the app-agnostic one. This app is pre-launch — there's
        # no real production data behind this switch, so the simplest correct
        # move is to drop and recreate rather than carry a translation path
        # for a schema that was never live. Detected by the presence of the
        # old `tool` column.
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(benchmarks)")}
        if 'tool' in existing_cols:
            conn.execute("DROP TABLE benchmarks")
        conn.executescript(_CREATE_SQLITE)
        conn.commit()
        conn.close()


def _fetchone_dict(conn, sql, params):
    ph = _placeholder()
    sql = sql.replace('?', ph) if ENV == 'production' else sql
    if ENV == 'production':
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
        return row
    else:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def _fetchall_dict(conn, sql, params):
    ph = _placeholder()
    sql = sql.replace('?', ph) if ENV == 'production' else sql
    if ENV == 'production':
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return list(rows)
    else:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def _execute(sql, params):
    ph = _placeholder()
    sql = sql.replace('?', ph) if ENV == 'production' else sql
    conn = _get_conn()
    try:
        if ENV == 'production':
            with conn.cursor() as cur:
                cur.execute(sql, params)
                last_id = cur.lastrowid
            conn.commit()
        else:
            cur = conn.execute(sql, params)
            last_id = cur.lastrowid
            conn.commit()
        return last_id
    finally:
        conn.close()


# ─── CRUD for the admin UI ─────────────────────────────────────────────────────

def list_benchmarks(metric=None, sector=None):
    conn = _get_conn()
    try:
        sql = "SELECT * FROM benchmarks WHERE 1=1"
        params = []
        if metric:
            sql += " AND metric = ?"
            params.append(metric)
        if sector:
            sql += " AND sector = ?"
            params.append(sector)
        sql += " ORDER BY metric, sector, geo, revenue_band"
        return _fetchall_dict(conn, sql, tuple(params))
    finally:
        conn.close()


def get_benchmark(benchmark_id):
    conn = _get_conn()
    try:
        return _fetchone_dict(conn, "SELECT * FROM benchmarks WHERE id = ?", (benchmark_id,))
    finally:
        conn.close()


def upsert_benchmark(data, benchmark_id=None):
    """Insert a new row, or update one if benchmark_id is given. Returns the row id.
    Relies on the UNIQUE(metric, sector, geo, revenue_band) constraint to catch
    accidental duplicate combinations on insert."""
    fields = ('metric', 'sector', 'geo', 'revenue_band', 'benchmark_value',
              'sample_size', 'source', 'effective_date', 'created_by')
    values = [data.get(f) for f in fields]

    if benchmark_id:
        set_clause = ', '.join(f"{f} = ?" for f in fields)
        _execute(
            f"UPDATE benchmarks SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(values) + (benchmark_id,),
        )
        return benchmark_id
    else:
        cols = ', '.join(fields)
        phs = ', '.join(['?'] * len(fields))
        return _execute(f"INSERT INTO benchmarks ({cols}) VALUES ({phs})", tuple(values))


def delete_benchmark(benchmark_id):
    _execute("DELETE FROM benchmarks WHERE id = ?", (benchmark_id,))


# ─── Read API used by OMI / omi-deepdive ───────────────────────────────────────

def _query_exact(conn, metric, sector, geo, revenue_band):
    return _fetchone_dict(
        conn,
        "SELECT * FROM benchmarks WHERE metric = ? AND sector = ? AND geo = ? AND revenue_band = ?",
        (metric, sector, geo, revenue_band),
    )


def find_benchmark(metric, sector=None, geo=None, revenue_band=None):
    """Look up one metric's benchmark for the given peer group, relaxing the
    least-fundamental axes first when the exact combination has no data:
    revenue_band -> geo -> sector -> fully global. Returns (row, matched) where
    `matched` records which of the caller's requested axes actually held after
    relaxation, so the caller can be honest about what's being compared
    ("peers in Banking" vs "peers in Banking, India" if revenue had to give)."""
    sector = sector or ALL_SECTORS
    geo = geo or ALL_GEOS
    revenue_band = revenue_band or ALL_REVENUE_BANDS

    attempts = [
        (sector, geo, revenue_band),
        (sector, geo, ALL_REVENUE_BANDS),
        (sector, ALL_GEOS, ALL_REVENUE_BANDS),
        (ALL_SECTORS, ALL_GEOS, ALL_REVENUE_BANDS),
    ]
    conn = _get_conn()
    try:
        seen = set()
        for s, g, r in attempts:
            key = (s, g, r)
            if key in seen:
                continue
            seen.add(key)
            row = _query_exact(conn, metric, s, g, r)
            if row:
                return row, {
                    'sector_matched': s == sector,
                    'geo_matched': g == geo,
                    'revenue_matched': r == revenue_band,
                }
        return None, None
    finally:
        conn.close()


def find_all_benchmarks(sector=None, geo=None, revenue_band=None):
    """Every canonical metric at once for one peer group (one call covers a
    full report). Callers translate canonical metric ids to their own
    domain/dimension ids — see OMI_METRIC_TO_CANONICAL / DEEPDIVE_METRIC_TO_CANONICAL
    in each app's own backend/app.py."""
    result = {}
    for metric_id, _label in METRICS:
        row, matched = find_benchmark(metric_id, sector, geo, revenue_band)
        if row:
            result[metric_id] = {
                'benchmark_value': row['benchmark_value'],
                'sample_size': row['sample_size'],
                'sector': row['sector'],
                'geo': row['geo'],
                'revenue_band': row['revenue_band'],
                'matched': matched,
            }
    return result
