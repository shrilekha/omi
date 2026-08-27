import os
import json
import sqlite3

ENV = os.getenv('ENV', 'development')

# Resolve project root robustly regardless of how Python was invoked
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# SQLite CREATE TABLE (auto-created on first run in dev)
_CREATE_SQLITE = """
CREATE TABLE IF NOT EXISTS submissions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT NOT NULL UNIQUE,
    submitted_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    email            TEXT NOT NULL,
    first_name       TEXT,
    last_name        TEXT,
    role             TEXT,
    sector           TEXT,
    country          TEXT,
    revenue_band     TEXT,
    sector_archetype TEXT,
    question_variant TEXT,
    domain_tools     TEXT,
    txn1 INTEGER, txn2 INTEGER, txn3 INTEGER, txn4 INTEGER, txn5 INTEGER,
    app1 INTEGER, app2 INTEGER, app3 INTEGER, app4 INTEGER, app5 INTEGER,
    infra1 INTEGER, infra2 INTEGER, infra3 INTEGER, infra4 INTEGER, infra5 INTEGER,
    log1 INTEGER, log2 INTEGER, log3 INTEGER, log4 INTEGER, log5 INTEGER,
    comp1 INTEGER, comp2 INTEGER, comp3 INTEGER, comp4 INTEGER, comp5 INTEGER,
    txn_score    REAL,
    app_score    REAL,
    infra_score  REAL,
    log_score    REAL,
    comp_score   REAL,
    overall_score REAL,
    maturity_band TEXT
);

CREATE TABLE IF NOT EXISTS admin_users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL UNIQUE,
    role        TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

_ANSWER_COLS = [
    'txn1','txn2','txn3','txn4','txn5',
    'app1','app2','app3','app4','app5',
    'infra1','infra2','infra3','infra4','infra5',
    'log1','log2','log3','log4','log5',
    'comp1','comp2','comp3','comp4','comp5',
]


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
        conn.executescript(_CREATE_SQLITE)
        existing_cols = {row[1] for row in conn.execute('PRAGMA table_info(submissions)')}
        if 'tools' in existing_cols and 'domain_tools' not in existing_cols:
            conn.execute('ALTER TABLE submissions RENAME COLUMN tools TO domain_tools')
        elif 'domain_tools' not in existing_cols:
            conn.execute('ALTER TABLE submissions ADD COLUMN domain_tools TEXT')
        if 'revenue_band' not in existing_cols:
            conn.execute('ALTER TABLE submissions ADD COLUMN revenue_band TEXT')
        conn.commit()
        conn.close()


def save_submission(data):
    answers = data.get('answers', {})
    scores  = data.get('scores', {})

    row = {
        'session_id':       data.get('session_id', ''),
        'email':            data.get('email', ''),
        'first_name':       data.get('first_name', ''),
        'last_name':        data.get('last_name', ''),
        'role':             data.get('role', ''),
        'sector':           data.get('sector', ''),
        'country':          data.get('country', ''),
        'revenue_band':     data.get('revenue_band', ''),
        'sector_archetype': data.get('sector_archetype', ''),
        'question_variant': data.get('question_variant', ''),
        'domain_tools':     json.dumps(data.get('domain_tools') or {}),
        'txn_score':        scores.get('txn', {}).get('pct'),
        'app_score':        scores.get('app', {}).get('pct'),
        'infra_score':      scores.get('infra', {}).get('pct'),
        'log_score':        scores.get('log', {}).get('pct'),
        'comp_score':       scores.get('comp', {}).get('pct'),
        'overall_score':    scores.get('overall'),
        'maturity_band':    data.get('maturity_band', ''),
    }
    for col in _ANSWER_COLS:
        val = answers.get(col)
        row[col] = val if isinstance(val, (int, float)) else None

    ph = _placeholder()
    cols   = list(row.keys())
    values = list(row.values())
    sql = f"INSERT OR IGNORE INTO submissions ({', '.join(cols)}) VALUES ({', '.join([ph]*len(cols))})"
    if ENV == 'production':
        sql = sql.replace('INSERT OR IGNORE', 'INSERT IGNORE')

    conn = _get_conn()
    try:
        if ENV == 'production':
            with conn.cursor() as cur:
                cur.execute(sql, values)
            conn.commit()
        else:
            conn.execute(sql, values)
            conn.commit()
    finally:
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
            conn.commit()
        else:
            conn.execute(sql, params)
            conn.commit()
    finally:
        conn.close()


# ─── Admin users (internal RBAC) ───────────────────────────────────────────────
# Distinct from ADMIN_KEY (a shared password, no per-user identity) and from
# Google OAuth (identity) — a verified Google identity with no active row here,
# and not covered by INITIAL_ADMIN_EMAILS at bootstrap, cannot reach any /admin
# route that requires a specific role. In ADMIN_KEY mode there's no per-user
# identity to check a role against, so require_role() falls back to full access.

def get_admin_user(email):
    conn = _get_conn()
    try:
        return _fetchone_dict(
            conn, "SELECT * FROM admin_users WHERE email = ? AND is_active = 1", (email,)
        )
    finally:
        conn.close()


def list_admin_users():
    conn = _get_conn()
    try:
        return _fetchall_dict(conn, "SELECT * FROM admin_users ORDER BY created_at", ())
    finally:
        conn.close()


def upsert_admin_user(email, role):
    conn = _get_conn()
    try:
        existing = _fetchone_dict(conn, "SELECT id FROM admin_users WHERE email = ?", (email,))
    finally:
        conn.close()
    if existing:
        _execute("UPDATE admin_users SET role = ?, is_active = 1 WHERE email = ?", (role, email))
    else:
        _execute(
            "INSERT INTO admin_users (email, role, is_active) VALUES (?, ?, 1)", (email, role)
        )


def deactivate_admin_user(email):
    _execute("UPDATE admin_users SET is_active = 0 WHERE email = ?", (email,))
