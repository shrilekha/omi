import json
import os
import secrets
import sys
import urllib.parse
import urllib.request
from functools import wraps
from io import BytesIO

import requests
from flask import (
    Flask, send_from_directory, request, jsonify,
    render_template, redirect, url_for, session, abort, send_file,
)
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/). override=True so this
# app's own .env always wins over a same-named var already sitting in the shell
# environment (e.g. PORT leaked in from another of this repo's apps started
# earlier in the same terminal) — these are independently configured apps that
# just happen to often run side by side on one machine.
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
# load_dotenv() silently does nothing if ENV_PATH doesn't exist (no error, no
# warning) — ENV_LOADED records which happened so the startup print below can
# say so honestly, instead of claiming a config file loaded when nothing did.
ENV_LOADED = load_dotenv(ENV_PATH, override=True)

from db import (
    init_db, save_submission,
    get_admin_user, list_admin_users, upsert_admin_user, deactivate_admin_user,
)
from email_sender import send_report_email
from questions_excel import build_workbook, read_workbook_file, apply_import, load_questions
from reports import get_report_data, get_filter_options, build_report_workbook

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
ADMIN_STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
# The public static_folder above is repurposed to serve frontend/ at '/', so
# templates' url_for('static', ...) would otherwise resolve into frontend/ too
# — this app's own admin CSS lives separately and needs its own static route.
app.add_url_rule(
    '/admin/static/<path:filename>', endpoint='admin_static',
    view_func=lambda filename: send_from_directory(ADMIN_STATIC_DIR, filename),
)
# Trust X-Forwarded-Host/-Proto/-For/-Port from the reverse proxy in front of
# this app (GitHub Codespaces' port forwarding, Nginx in production, etc.) so
# the Google OAuth redirect_uri built from request.url_root is the URL a
# browser can actually reach, not whatever Host header the proxy passes
# through to this container.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

ADMIN_KEY = os.getenv('ADMIN_KEY', 'changeme-admin-password')

# Admin login via Google OAuth — off by default. Set both GOOGLE_OAUTH_CLIENT_ID
# and GOOGLE_OAUTH_CLIENT_SECRET (see .env.example) to switch admin login from
# the ADMIN_KEY password to "Sign in with Google" — no code changes needed.
# Implemented with stdlib urllib against Google's OAuth endpoints directly (no
# Authlib/google-auth dependency — the google-auth/google-api-python-client
# packages already in requirements.txt are for Gmail-sending, a separate,
# unrelated mechanism), mirroring omi-deepdive's identical setup.
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '').strip()
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '').strip()
GOOGLE_ALLOWED_DOMAIN = os.getenv('GOOGLE_OAUTH_ALLOWED_DOMAIN', '').strip().lower()
OAUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://openidconnect.googleapis.com/v1/userinfo'

OAUTH_LOGIN_ERRORS = {
    'oauth_failed': 'Google sign-in failed. Please try again.',
    'oauth_unverified': "That Google account's email is not verified.",
    'oauth_domain': 'That Google account is not authorized for this tool.',
    'not_authorized': "That Google account isn't set up in this tool yet. "
                       "Contact an admin to be added.",
}

# ─── Internal RBAC ──────────────────────────────────────────────────────────
# OMI's own two admin capabilities — not a copy of omi-deepdive's org-management
# roles. Only meaningful once Google OAuth is enabled; in ADMIN_KEY-only mode
# there's no per-user identity to check a role against, so require_role() below
# falls back to full access for anyone who has the shared key.
ROLE_ADMIN = 'admin'
ROLE_CONTENT_EDITOR = 'content_editor'
ROLE_ANALYST = 'analyst'
ALL_ROLES = [ROLE_ADMIN, ROLE_CONTENT_EDITOR, ROLE_ANALYST]
QUESTIONS_ROLES = (ROLE_ADMIN, ROLE_CONTENT_EDITOR)
REPORTS_ROLES = (ROLE_ADMIN, ROLE_ANALYST)

# Comma-separated emails allowed to bootstrap themselves as the first admin(s)
# the first time they sign in with Google, before admin_users has any rows.
INITIAL_ADMIN_EMAILS = {
    e.strip().lower() for e in os.getenv('INITIAL_ADMIN_EMAILS', '').split(',') if e.strip()
}


def require_role(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get('admin'):
                return redirect(url_for('admin_login', next=request.path))
            if OAUTH_ENABLED and session.get('admin_role') not in roles:
                return render_template('admin_forbidden.html', required_roles=roles), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


# omi-benchmarks is a separate service (see ../omi-benchmarks). This backend
# proxies to it server-to-server so the shared API key never reaches the
# browser, and so the browser only ever talks to same-origin /api/*.
BENCHMARKS_URL = os.getenv('BENCHMARKS_URL', '').rstrip('/')
BENCHMARKS_API_KEY = os.getenv('BENCHMARKS_API_KEY', '')

# omi-benchmarks stores figures against an app-agnostic capability-area id
# (see omi-benchmarks/backend/constants.py METRICS) so the same number can
# be entered once and read by both OMI and omi-deepdive — this maps OMI's
# own 5 domain ids onto those canonical ids. `comp` has no canonical
# counterpart requested by omi-deepdive, which is fine; it's still one of
# the canonical metrics, just one only OMI ever asks for.
OMI_METRIC_TO_CANONICAL = {
    'overall': 'overall', 'txn': 'txn', 'app': 'app_perf', 'infra': 'infra_network',
    'log': 'log', 'comp': 'compliance',
}
CANONICAL_TO_OMI_METRIC = {v: k for k, v in OMI_METRIC_TO_CANONICAL.items()}

# omi-benchmarks' geo axis is deliberately coarser than OMI's own country
# dropdown (which drives real question-content differences — Middle East
# gets a GCC regulatory variant, everyone else non-India gets _intl). This
# collapses OMI's finer country value down to omi-benchmarks' 3 buckets
# before every /api/benchmarks call — see the comment on GEOS in
# omi-benchmarks/backend/constants.py for why.
OMI_COUNTRY_TO_BENCHMARK_GEO = {
    'India': 'India', 'Middle East': 'Middle East',
    'Singapore': 'International', 'United Kingdom': 'International',
    'United States': 'International', 'Australia': 'International', 'Other': 'International',
}


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json(silent=True) or {}
    try:
        save_submission(data)
        send_report_email(data)
    except Exception as e:
        app.logger.error(f'Submission error: {e}')
    return jsonify({'status': 'ok'})


@app.route('/api/benchmarks')
def benchmarks_proxy():
    # Never let a benchmarks-service outage or missing config break the
    # report — the peer-comparison card just has nothing to show, silently.
    if not BENCHMARKS_URL:
        return jsonify({})

    params = {}
    sector = request.args.get('sector', '')
    if sector:
        params['sector'] = sector
    geo = request.args.get('geo', '')
    if geo:
        params['geo'] = OMI_COUNTRY_TO_BENCHMARK_GEO.get(geo, 'International')
    revenue_band = request.args.get('revenue_band', '')
    if revenue_band:
        params['revenue_band'] = revenue_band

    try:
        resp = requests.get(
            f'{BENCHMARKS_URL}/api/benchmarks', params=params,
            headers={'X-Api-Key': BENCHMARKS_API_KEY}, timeout=5,
        )
        canonical_data = resp.json() if resp.ok else {}
    except (requests.RequestException, ValueError) as e:
        app.logger.warning(f'benchmarks proxy error: {e}')
        canonical_data = {}

    # Translate canonical capability-area ids back to OMI's own domain ids
    # so the frontend can key straight off scores.<domain>.pct as before.
    result = {}
    for canonical_id, payload in canonical_data.items():
        omi_id = CANONICAL_TO_OMI_METRIC.get(canonical_id)
        if omi_id:
            result[omi_id] = payload
    return jsonify(result)


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'env': os.getenv('ENV', 'development')})


# ─── Admin: auth ────────────────────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET' and session.get('admin'):
        return redirect(url_for('admin_questions'))

    error = OAUTH_LOGIN_ERRORS.get(request.args.get('error'))

    if OAUTH_ENABLED:
        # Password login is retired once Google OAuth is configured — this is
        # a swap, not an additional parallel login path.
        if request.method == 'POST':
            abort(404)
        return render_template('admin_login.html', error=error, oauth_enabled=True)

    if request.method == 'POST':
        if request.form.get('key') == ADMIN_KEY:
            session['admin'] = True
            session['admin_role'] = ROLE_ADMIN
            return redirect(request.args.get('next') or url_for('admin_questions'))
        error = 'Incorrect key.'
    return render_template('admin_login.html', error=error, oauth_enabled=False)


@app.route('/admin/google/login')
def admin_google_login():
    if not OAUTH_ENABLED:
        abort(404)
    state = secrets.token_urlsafe(24)
    session['oauth_state'] = state
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': url_for('admin_google_callback', _external=True),
        'response_type': 'code',
        'scope': 'openid email',
        'state': state,
        'prompt': 'select_account',
    }
    if GOOGLE_ALLOWED_DOMAIN:
        params['hd'] = GOOGLE_ALLOWED_DOMAIN
    return redirect(f'{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}')


@app.route('/admin/google/callback')
def admin_google_callback():
    if not OAUTH_ENABLED:
        abort(404)

    if not request.args.get('state') or request.args.get('state') != session.pop('oauth_state', None):
        return redirect(url_for('admin_login', error='oauth_failed'))

    code = request.args.get('code')
    if not code:
        return redirect(url_for('admin_login', error='oauth_failed'))

    try:
        token_body = urllib.parse.urlencode({
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': url_for('admin_google_callback', _external=True),
            'grant_type': 'authorization_code',
        }).encode()
        token_req = urllib.request.Request(GOOGLE_TOKEN_URL, data=token_body, method='POST')
        with urllib.request.urlopen(token_req, timeout=10) as resp:
            access_token = json.loads(resp.read().decode())['access_token']

        userinfo_req = urllib.request.Request(
            GOOGLE_USERINFO_URL, headers={'Authorization': f'Bearer {access_token}'}
        )
        with urllib.request.urlopen(userinfo_req, timeout=10) as resp:
            userinfo = json.loads(resp.read().decode())
    except Exception as e:
        app.logger.error(f'Google OAuth error: {e}')
        return redirect(url_for('admin_login', error='oauth_failed'))

    email = (userinfo.get('email') or '').strip()
    if not email or not userinfo.get('email_verified'):
        return redirect(url_for('admin_login', error='oauth_unverified'))

    if GOOGLE_ALLOWED_DOMAIN and not email.lower().endswith('@' + GOOGLE_ALLOWED_DOMAIN):
        return redirect(url_for('admin_login', error='oauth_domain'))

    # Identity (verified Google email) is not the same as authorization — the
    # email must also carry a role, either already granted in admin_users or
    # matched against the one-time bootstrap list below.
    admin_user = get_admin_user(email)
    if admin_user:
        role = admin_user['role']
    elif email.lower() in INITIAL_ADMIN_EMAILS:
        upsert_admin_user(email, ROLE_ADMIN)
        role = ROLE_ADMIN
    else:
        return redirect(url_for('admin_login', error='not_authorized'))

    session['admin'] = True
    session['admin_email'] = email
    session['admin_role'] = role
    return redirect(url_for('admin_questions'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/users', methods=['GET', 'POST'])
@require_role(ROLE_ADMIN)
def admin_users_page():
    error = None
    if request.method == 'POST':
        action = request.form.get('action')
        email = (request.form.get('email') or '').strip().lower()
        if action == 'add':
            role = request.form.get('role')
            if role not in ALL_ROLES:
                error = 'Invalid role.'
            elif not email:
                error = 'Email is required.'
            else:
                upsert_admin_user(email, role)
        elif action == 'deactivate' and email:
            deactivate_admin_user(email)

    return render_template(
        'admin_users.html', users=list_admin_users(), roles=ALL_ROLES,
        oauth_enabled=OAUTH_ENABLED, error=error, active='users',
    )


# ─── Admin: questions (Excel export/import) ────────────────────────────────

@app.route('/admin/questions')
@require_role(*QUESTIONS_ROLES)
def admin_questions():
    txn, comp, app_q, infra_q, log_q = load_questions()
    counts = {
        'txn': sum(len(v) for v in txn.values()),
        'comp': sum(len(v) for v in comp.values()),
        'app': len(app_q), 'infra': len(infra_q), 'log': len(log_q),
    }
    counts['total'] = sum(counts.values())
    return render_template(
        'admin_questions.html', counts=counts,
        import_result=session.pop('questions_import_result', None), active='questions',
    )


@app.route('/admin/questions/export')
@require_role(*QUESTIONS_ROLES)
def admin_questions_export():
    buf = BytesIO()
    build_workbook().save(buf)
    buf.seek(0)
    return send_file(
        buf, as_attachment=True, download_name='OMI_Questions_Review.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@app.route('/admin/questions/import', methods=['POST'])
@require_role(*QUESTIONS_ROLES)
def admin_questions_import():
    """All-or-nothing, unlike the benchmarks import: questions.js is one
    generated file, so a partial write would leave it in a state nobody
    asked for. Any bad row blocks the whole write and is reported."""
    file = request.files.get('file')
    if not file or not file.filename:
        session['questions_import_result'] = {'errors': ['No file selected.'], 'diff': []}
        return redirect(url_for('admin_questions'))

    try:
        txn, comp, app_q, infra_q, log_q, errors = read_workbook_file(file)
    except Exception:
        session['questions_import_result'] = {
            'errors': [f'Could not read "{file.filename}" — is it a valid .xlsx workbook?'],
            'diff': [],
        }
        return redirect(url_for('admin_questions'))

    if errors:
        session['questions_import_result'] = {'errors': errors, 'diff': []}
    else:
        diff = apply_import(txn, comp, app_q, infra_q, log_q)
        session['questions_import_result'] = {'errors': [], 'diff': diff}

    return redirect(url_for('admin_questions'))


# ─── Admin: reports (submission-data analytics — OMI's own data, not synced
# with or dependent on omi-benchmarks) ──────────────────────────────────────

def _filtered_report_data():
    filters = {
        'sector': request.args.get('sector', '').strip(),
        'country': request.args.get('country', '').strip(),
        'revenue_band': request.args.get('revenue_band', '').strip(),
        'date_from': request.args.get('date_from', '').strip(),
        'date_to': request.args.get('date_to', '').strip(),
    }
    data = get_report_data(
        sector=filters['sector'] or None, country=filters['country'] or None,
        revenue_band=filters['revenue_band'] or None,
        date_from=filters['date_from'] or None, date_to=filters['date_to'] or None,
    )
    return filters, data


@app.route('/admin/reports')
@require_role(*REPORTS_ROLES)
def admin_reports():
    filters, data = _filtered_report_data()
    return render_template(
        'admin_reports.html', data=data, filters=filters,
        filter_options=get_filter_options(), active='reports',
    )


@app.route('/admin/reports/export.xlsx')
@require_role(*REPORTS_ROLES)
def admin_reports_export():
    filters, data = _filtered_report_data()
    buf = BytesIO()
    build_report_workbook(data, filters).save(buf)
    buf.seek(0)
    return send_file(
        buf, as_attachment=True, download_name='OMI_Report.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@app.route('/admin/reports/print')
@require_role(*REPORTS_ROLES)
def admin_reports_print():
    filters, data = _filtered_report_data()
    return render_template('admin_reports_print.html', data=data, filters=filters)


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5050))
    where = f'http://localhost:{port}' if debug else f'port {port}'
    print(f'\n  OMI running at {where}')
    if ENV_LOADED:
        print(f'  Config loaded from {os.path.abspath(ENV_PATH)}\n')
    else:
        abs_path = os.path.abspath(ENV_PATH)
        print(f'  No .env found at {abs_path} — using process environment and '
              f'defaults only. Run: cp {abs_path}.example {abs_path}\n')
    app.run(debug=debug, port=port)
