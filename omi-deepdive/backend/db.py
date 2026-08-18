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
    overall_score          REAL,
    maturity_band          TEXT,
    submitted_at           DATETIME DEFAULT CURRENT_TIMESTAMP
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


def create_organization(name):
    token = _new_token()
    conn = _get_conn()
    try:
        ph = _placeholder()
        sql = f"INSERT INTO organizations (name, report_token) VALUES ({ph}, {ph})"
        if ENV == 'production':
            with conn.cursor() as cur:
                cur.execute(sql, (name, token))
                org_id = cur.lastrowid
            conn.commit()
        else:
            cur = conn.execute(sql, (name, token))
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
