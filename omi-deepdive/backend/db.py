import os
import json
import secrets
import sqlite3

ENV = os.getenv('ENV', 'development')

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

_CREATE_SQLITE = """
CREATE TABLE IF NOT EXISTS organizations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    report_token  TEXT NOT NULL UNIQUE,
    sector        TEXT NOT NULL DEFAULT 'all',
    geo           TEXT NOT NULL DEFAULT 'all',
    revenue_band  TEXT NOT NULL DEFAULT 'all',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS apps (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id  INTEGER NOT NULL,
    name             TEXT NOT NULL,
    owner_name       TEXT,
    owner_email      TEXT,
    criticality      TEXT,
    access_token     TEXT NOT NULL UNIQUE,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS submissions (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id                 INTEGER NOT NULL,
    session_id             TEXT NOT NULL UNIQUE,
    respondent_name        TEXT,
    respondent_email       TEXT,
    respondent_role        TEXT,
    owner_contact          TEXT,
    biggest_blocker        TEXT,
    answers_json           TEXT NOT NULL,
    tools_json             TEXT NOT NULL,
    dimension_scores_json  TEXT NOT NULL,
    na_dims_json           TEXT NOT NULL DEFAULT '[]',
    overall_score          REAL,
    maturity_band          TEXT,
    submitted_at           DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL UNIQUE,
    role        TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
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
        conn.executescript(_CREATE_SQLITE)
        existing_cols = {row[1] for row in conn.execute('PRAGMA table_info(organizations)')}
        for col in ('sector', 'geo', 'revenue_band'):
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE organizations ADD COLUMN {col} TEXT NOT NULL DEFAULT 'all'")
        conn.commit()
        conn.close()


def _new_token():
    return secrets.token_urlsafe(24)


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


def create_organization(name, sector='all', geo='all', revenue_band='all'):
    token = _new_token()
    conn = _get_conn()
    try:
        ph = _placeholder()
        sql = (f"INSERT INTO organizations (name, report_token, sector, geo, revenue_band) "
               f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph})")
        params = (name, token, sector, geo, revenue_band)
        if ENV == 'production':
            with conn.cursor() as cur:
                cur.execute(sql, params)
                org_id = cur.lastrowid
            conn.commit()
        else:
            cur = conn.execute(sql, params)
            org_id = cur.lastrowid
            conn.commit()
        return org_id, token
    finally:
        conn.close()


def create_app(organization_id, name, owner_name='', owner_email='', criticality=''):
    token = _new_token()
    conn = _get_conn()
    try:
        ph = _placeholder()
        sql = (f"INSERT INTO apps (organization_id, name, owner_name, owner_email, "
               f"criticality, access_token) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})")
        params = (organization_id, name, owner_name, owner_email, criticality, token)
        if ENV == 'production':
            with conn.cursor() as cur:
                cur.execute(sql, params)
                app_id = cur.lastrowid
            conn.commit()
        else:
            cur = conn.execute(sql, params)
            app_id = cur.lastrowid
            conn.commit()
        return app_id, token
    finally:
        conn.close()


def get_app_by_token(token):
    conn = _get_conn()
    try:
        row = _fetchone_dict(
            conn,
            "SELECT a.*, o.name AS org_name, o.id AS org_id "
            "FROM apps a JOIN organizations o ON a.organization_id = o.id "
            "WHERE a.access_token = ?",
            (token,),
        )
        return row
    finally:
        conn.close()


def get_org_by_report_token(token):
    conn = _get_conn()
    try:
        return _fetchone_dict(conn, "SELECT * FROM organizations WHERE report_token = ?", (token,))
    finally:
        conn.close()


def get_organization(organization_id):
    conn = _get_conn()
    try:
        return _fetchone_dict(conn, "SELECT * FROM organizations WHERE id = ?", (organization_id,))
    finally:
        conn.close()


def get_all_organizations():
    conn = _get_conn()
    try:
        return _fetchall_dict(conn, "SELECT * FROM organizations ORDER BY created_at DESC", ())
    finally:
        conn.close()


def count_organizations():
    conn = _get_conn()
    try:
        row = _fetchone_dict(conn, "SELECT COUNT(*) AS n FROM organizations", ())
        return row['n'] if row else 0
    finally:
        conn.close()


def get_organizations_page(limit, offset):
    conn = _get_conn()
    try:
        return _fetchall_dict(
            conn,
            "SELECT * FROM organizations ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
    finally:
        conn.close()


def get_app(app_id):
    conn = _get_conn()
    try:
        return _fetchone_dict(conn, "SELECT * FROM apps WHERE id = ?", (app_id,))
    finally:
        conn.close()


def delete_submissions_for_app(app_id):
    conn = _get_conn()
    try:
        ph = _placeholder()
        sql = f"DELETE FROM submissions WHERE app_id = {ph}"
        if ENV == 'production':
            with conn.cursor() as cur:
                cur.execute(sql, (app_id,))
            conn.commit()
        else:
            conn.execute(sql, (app_id,))
            conn.commit()
    finally:
        conn.close()


def delete_submissions_for_org(organization_id):
    conn = _get_conn()
    try:
        app_ids = [a['id'] for a in _fetchall_dict(
            conn, "SELECT id FROM apps WHERE organization_id = ?", (organization_id,)
        )]
    finally:
        conn.close()
    for app_id in app_ids:
        delete_submissions_for_app(app_id)


def get_apps_for_org(organization_id):
    conn = _get_conn()
    try:
        return _fetchall_dict(
            conn, "SELECT * FROM apps WHERE organization_id = ? ORDER BY id", (organization_id,)
        )
    finally:
        conn.close()


def get_latest_submission(app_id):
    conn = _get_conn()
    try:
        row = _fetchone_dict(
            conn,
            "SELECT * FROM submissions WHERE app_id = ? ORDER BY submitted_at DESC, id DESC LIMIT 1",
            (app_id,),
        )
        if row:
            row = dict(row)
            row['answers'] = json.loads(row['answers_json'])
            row['tools'] = json.loads(row['tools_json'])
            row['dimension_scores'] = json.loads(row['dimension_scores_json'])
            row['na_dims'] = json.loads(row['na_dims_json'] or '[]')
        return row
    finally:
        conn.close()


def save_submission(app_id, data):
    ph = _placeholder()
    row = {
        'app_id': app_id,
        'session_id': data['session_id'],
        'respondent_name': data.get('respondent_name', ''),
        'respondent_email': data.get('respondent_email', ''),
        'respondent_role': data.get('respondent_role', ''),
        'owner_contact': data.get('owner_contact', ''),
        'biggest_blocker': data.get('biggest_blocker', ''),
        'answers_json': json.dumps(data.get('answers', {})),
        'tools_json': json.dumps(data.get('tools', {})),
        'dimension_scores_json': json.dumps(data.get('dimension_scores', {})),
        'na_dims_json': json.dumps(data.get('na_dims', [])),
        'overall_score': data.get('overall_score'),
        'maturity_band': data.get('maturity_band', ''),
    }
    cols = list(row.keys())
    values = list(row.values())
    sql = f"INSERT INTO submissions ({', '.join(cols)}) VALUES ({', '.join([ph]*len(cols))})"

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
# Distinct from Google OAuth (identity) and from apps.access_token (external
# respondent access, no login, no role). A Google identity with no active row
# here — and not covered by INITIAL_ADMIN_EMAILS at bootstrap — cannot reach
# any /admin or /dashboard route.

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
