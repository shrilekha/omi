import json
import os
import re
import secrets
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from functools import wraps
from io import BytesIO
import requests
from flask import Flask, render_template, request, redirect, url_for, abort, session, send_file
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# override=True so this app's own .env always wins over a same-named var already
# sitting in the shell environment (e.g. PORT leaked in from another of this
# repo's apps started earlier in the same terminal).
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', '.env')
# load_dotenv() silently does nothing if ENV_PATH doesn't exist (no error, no
# warning) — ENV_LOADED records which happened so the startup print below can
# say so honestly, instead of claiming a config file loaded when nothing did.
ENV_LOADED = load_dotenv(ENV_PATH, override=True)

from db import (
    init_db, get_app_by_token, get_org_by_report_token, get_apps_for_org,
    get_latest_submission, save_submission, create_organization, create_app,
    get_organization, get_all_organizations, get_app, delete_submissions_for_app,
    delete_submissions_for_org, count_organizations, get_organizations_page,
    get_admin_user, list_admin_users, upsert_admin_user, deactivate_admin_user,
)
from scoring import compute_scores
from questions import DIMENSIONS, OWNERSHIP_QUESTIONS
from constants import SECTORS, GEOS, REVENUE_BANDS
from questions_excel import build_workbook, read_workbook_file, apply_import, load_current

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
ADMIN_KEY = os.getenv('ADMIN_KEY', 'changeme-admin-password')

# omi-benchmarks is a separate service (see ../omi-benchmarks). This backend
# proxies to it server-side — the organization's sector/geo/revenue is fixed
# at org-creation time, so unlike OMI there's no picker; reports just show
# whatever peer comparison that org's stored traits resolve to.
BENCHMARKS_URL = os.getenv('BENCHMARKS_URL', '').rstrip('/')
BENCHMARKS_API_KEY = os.getenv('BENCHMARKS_API_KEY', '')


def _label(options, value):
    return dict(options).get(value) if value and value != 'all' else None


# omi-benchmarks stores figures against an app-agnostic capability-area id
# (see omi-benchmarks/backend/constants.py METRICS) so the same number can
# be entered once and read by both omi-deepdive and OMI — this maps
# omi-deepdive's own 8 dimension ids onto those canonical ids. 'network' and
# 'infra' BOTH map to 'infra_network' deliberately: OMI treats those as one
# combined domain, so both of deepdive's finer-grained dimensions compare
# against that same one figure. 'rum'/'synthetic'/'correlation' have no OMI
# counterpart, which is fine — they're still canonical metrics, just ones
# only omi-deepdive ever asks for.
DEEPDIVE_METRIC_TO_CANONICAL = {
    'overall': 'overall', 'biztxn': 'txn', 'apm': 'app_perf',
    'infra': 'infra_network', 'network': 'infra_network', 'logs': 'log',
    'rum': 'rum', 'synthetic': 'synthetic', 'correlation': 'correlation',
}


def get_org_benchmarks(org):
    """All deepdive dimensions' benchmarks for one org's stored sector/geo/
    revenue, or {} if the benchmarks service isn't configured, unreachable,
    or has nothing for this org yet — reports must render fine either way."""
    if not BENCHMARKS_URL:
        return {}
    params = {}
    for key in ('sector', 'geo', 'revenue_band'):
        value = org.get(key)
        if value and value != 'all':
            params[key] = value
    try:
        resp = requests.get(
            f'{BENCHMARKS_URL}/api/benchmarks', params=params,
            headers={'X-Api-Key': BENCHMARKS_API_KEY}, timeout=5,
        )
        canonical_data = resp.json() if resp.ok else {}
    except (requests.RequestException, ValueError) as e:
        app.logger.warning(f'benchmarks lookup failed: {e}')
        return {}

    # Translate canonical ids back to deepdive's own dimension ids — a
    # canonical hit can populate more than one dimension (infra_network ->
    # both 'infra' and 'network'), by design.
    result = {}
    for dim_id, canonical_id in DEEPDIVE_METRIC_TO_CANONICAL.items():
        if canonical_id in canonical_data:
            result[dim_id] = canonical_data[canonical_id]
    return result

# Admin login via Google OAuth — off by default. Set both GOOGLE_OAUTH_CLIENT_ID
# and GOOGLE_OAUTH_CLIENT_SECRET (see .env.example) to switch admin login from
# the ADMIN_KEY password to "Sign in with Google" — no code changes needed.
# Implemented with stdlib urllib against Google's OAuth endpoints directly
# (no Authlib/google-auth dependency) so enabling this later never requires a
# new pip install, only env vars.
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
# Only meaningful once Google OAuth is enabled (OAUTH_ENABLED above) — a
# verified Google identity is *identity*, not *authorization*; it must also
# carry one of these roles (admin_users table) to reach an internal route.
# In password-mode (ADMIN_KEY, no OAuth), there is no per-user identity to
# check a role against, so the shared key continues to grant full admin
# access as before — require_role() below falls back to that.
ROLE_ADMIN = 'admin'
ROLE_ASSESSMENT_MANAGER = 'assessment_manager'
ROLE_REVIEWER = 'reviewer'
ROLE_EXECUTIVE = 'executive'
ALL_ROLES = [ROLE_ADMIN, ROLE_ASSESSMENT_MANAGER, ROLE_REVIEWER, ROLE_EXECUTIVE]
MANAGE_ROLES = (ROLE_ADMIN, ROLE_ASSESSMENT_MANAGER)
VIEW_ROLES = (ROLE_ADMIN, ROLE_ASSESSMENT_MANAGER, ROLE_REVIEWER, ROLE_EXECUTIVE)

# Comma-separated emails allowed to bootstrap themselves as the first admin(s)
# the first time they sign in with Google, before admin_users has any rows.
INITIAL_ADMIN_EMAILS = {
    e.strip().lower() for e in os.getenv('INITIAL_ADMIN_EMAILS', '').split(',') if e.strip()
}

# Trust X-Forwarded-Host/-Proto/-For/-Port from the reverse proxy in front of
# this app (GitHub Codespaces' port forwarding, Nginx in production, etc.) so
# request.url_root — used to build the links shown on /admin/org/<id> — reflects
# the URL a browser can actually reach, not whatever Host header the proxy
# passes through to this container.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)


def _slug(text):
    return re.sub(r'_+', '_', re.sub(r'[^A-Za-z0-9]+', '_', text or '')).strip('_') or 'file'


def _pdf_filename(*parts):
    stamp = datetime.now().strftime('%d%b%Y')
    return '_'.join([_slug(p) for p in parts] + [stamp])


def require_role(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get('admin'):
                return redirect(url_for('admin_login', next=request.path))
            if OAUTH_ENABLED and session.get('admin_role') not in roles:
                return render_template(
                    'admin_forbidden.html', required_roles=roles
                ), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.route('/')
def index():
    return redirect(url_for('admin_login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET' and session.get('admin'):
        return redirect(url_for('admin_new'))

    error = OAUTH_LOGIN_ERRORS.get(request.args.get('error'))

    if OAUTH_ENABLED:
        # Password login is retired once Google OAuth is configured — this is a
        # swap, not an additional parallel login path.
        if request.method == 'POST':
            abort(404)
        return render_template('admin_login.html', error=error, oauth_enabled=True)

    if request.method == 'POST':
        if request.form.get('key') == ADMIN_KEY:
            session['admin'] = True
            session['admin_role'] = ROLE_ADMIN
            return redirect(request.args.get('next') or url_for('admin_new'))
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

    # Identity (verified Google email) is not the same as authorization —
    # the email must also carry a role, either already granted in admin_users
    # or matched against the one-time bootstrap list below.
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
    return redirect(url_for('admin_new'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    return redirect(url_for('admin_login'))


ORGS_PER_PAGE = 10


@app.route('/admin/new', methods=['GET', 'POST'])
@require_role(*MANAGE_ROLES)
def admin_new():
    ctx = {'sectors': SECTORS, 'geos': GEOS, 'revenue_bands': REVENUE_BANDS}
    if request.method == 'POST':
        org_name = request.form.get('org_name', '').strip()
        if not org_name:
            return render_template('admin_new.html', error='Organization name is required.', **ctx)

        app_names = [v.strip() for k, v in request.form.items() if k.startswith('app_name_') and v.strip()]
        if not app_names:
            return render_template('admin_new.html', error='At least one app name is required.', **ctx)

        sector = request.form.get('sector', 'all')
        geo = request.form.get('geo', 'all')
        revenue_band = request.form.get('revenue_band', 'all')
        org_id, _ = create_organization(org_name, sector=sector, geo=geo, revenue_band=revenue_band)
        for name in app_names:
            create_app(org_id, name)

        return redirect(url_for('admin_org', org_id=org_id))

    return render_template('admin_new.html', error=None, **ctx)


@app.route('/admin/orgs')
@require_role(*MANAGE_ROLES)
def admin_orgs():
    page = max(1, request.args.get('page', 1, type=int))
    total = count_organizations()
    total_pages = max(1, (total + ORGS_PER_PAGE - 1) // ORGS_PER_PAGE)
    page = min(page, total_pages)
    orgs = get_organizations_page(ORGS_PER_PAGE, (page - 1) * ORGS_PER_PAGE)
    return render_template('admin_orgs.html', orgs=orgs, page=page, total_pages=total_pages)


@app.route('/admin/org/<int:org_id>')
@require_role(*MANAGE_ROLES)
def admin_org(org_id):
    org = get_organization(org_id)
    if not org:
        abort(404)
    apps = get_apps_for_org(org_id)
    base_url = request.url_root.rstrip('/')
    return render_template('admin_org.html', org=org, apps=apps, base_url=base_url)


@app.route('/admin/app/<int:app_id>/reset', methods=['POST'])
@require_role(*MANAGE_ROLES)
def admin_reset_app(app_id):
    app_row = get_app(app_id)
    if not app_row:
        abort(404)
    delete_submissions_for_app(app_id)
    return redirect(url_for('admin_org', org_id=app_row['organization_id']))


@app.route('/admin/org/<int:org_id>/reset', methods=['POST'])
@require_role(*MANAGE_ROLES)
def admin_reset_org(org_id):
    org = get_organization(org_id)
    if not org:
        abort(404)
    delete_submissions_for_org(org_id)
    return redirect(url_for('admin_org', org_id=org_id))


@app.route('/admin/users', methods=['GET', 'POST'])
@require_role(ROLE_ADMIN)
def admin_users_page():
    error = None
    if request.method == 'POST':
        action = request.form.get('action')
        email = (request.form.get('email') or '').strip().lower()
        if action == 'add':
            role = request.form.get('role')
            if email and role in ALL_ROLES:
                upsert_admin_user(email, role)
            else:
                error = 'Enter a valid email and choose a role.'
        elif action == 'deactivate' and email:
            deactivate_admin_user(email)
    users = list_admin_users()
    return render_template(
        'admin_users.html', users=users, roles=ALL_ROLES, error=error,
        oauth_enabled=OAUTH_ENABLED,
    )


# ─── Admin: questions (Excel export/import) ────────────────────────────────

@app.route('/admin/questions')
@require_role(*MANAGE_ROLES)
def admin_questions():
    ownership, dimensions = load_current()
    counts = {d['id']: len(d['questions']) for d in dimensions}
    counts['total'] = sum(counts.values())
    return render_template(
        'admin_questions.html', dimensions=dimensions, counts=counts,
        import_result=session.pop('questions_import_result', None),
    )


@app.route('/admin/questions/export')
@require_role(*MANAGE_ROLES)
def admin_questions_export():
    buf = BytesIO()
    build_workbook().save(buf)
    buf.seek(0)
    return send_file(
        buf, as_attachment=True, download_name='omi-deepdive_Questions.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@app.route('/admin/questions/import', methods=['POST'])
@require_role(*MANAGE_ROLES)
def admin_questions_import():
    """All-or-nothing, same as OMI's: questions.py is one generated file
    (well, mostly generated — see questions_excel.py's merge logic), so a
    partial write would leave it in a state nobody asked for."""
    file = request.files.get('file')
    if not file or not file.filename:
        session['questions_import_result'] = {'errors': ['No file selected.'], 'diff': []}
        return redirect(url_for('admin_questions'))

    try:
        ownership_after, dims_after, errors = read_workbook_file(file)
    except Exception:
        session['questions_import_result'] = {
            'errors': [f'Could not read "{file.filename}" — is it a valid .xlsx workbook?'],
            'diff': [],
        }
        return redirect(url_for('admin_questions'))

    if errors:
        session['questions_import_result'] = {'errors': errors, 'diff': []}
    else:
        diff = apply_import(ownership_after, dims_after)
        session['questions_import_result'] = {'errors': [], 'diff': diff}

    return redirect(url_for('admin_questions'))


@app.route('/dashboard')
@require_role(*VIEW_ROLES)
def dashboard():
    page = max(1, request.args.get('page', 1, type=int))
    total = count_organizations()
    total_pages = max(1, (total + ORGS_PER_PAGE - 1) // ORGS_PER_PAGE)
    page = min(page, total_pages)
    orgs = get_organizations_page(ORGS_PER_PAGE, (page - 1) * ORGS_PER_PAGE)
    return render_template('dashboard.html', orgs=orgs, page=page, total_pages=total_pages)


@app.route('/app/<token>', methods=['GET', 'POST'])
def assess(token):
    app_row = get_app_by_token(token)
    if not app_row:
        abort(404)

    if request.method == 'POST':
        result = compute_scores(request.form)
        result['session_id'] = str(uuid.uuid4())
        result['respondent_name'] = request.form.get('respondent_name', '')
        result['respondent_email'] = request.form.get('respondent_email', '')
        result['respondent_role'] = request.form.get('respondent_role', '')
        result['owner_contact'] = request.form.get('owner_contact', '')
        result['biggest_blocker'] = request.form.get('biggest_blocker', '')
        save_submission(app_row['id'], result)
        pdf_filename = _pdf_filename(app_row['name'], app_row['org_name'])
        org = get_organization(app_row['org_id'])
        return render_template(
            'submission_summary.html', app_row=app_row, result=result, just_submitted=True,
            dimensions=DIMENSIONS, pdf_filename=pdf_filename, benchmarks=get_org_benchmarks(org),
            org_sector_label=_label(SECTORS, org['sector']), org_geo_label=_label(GEOS, org['geo']),
        )

    existing = get_latest_submission(app_row['id'])
    return render_template(
        'assess.html', app_row=app_row, dimensions=DIMENSIONS, ownership=OWNERSHIP_QUESTIONS,
        existing=existing,
    )


@app.route('/app/<token>/print')
def print_submission(token):
    app_row = get_app_by_token(token)
    if not app_row:
        abort(404)
    existing = get_latest_submission(app_row['id'])
    if not existing:
        abort(404)
    pdf_filename = _pdf_filename(app_row['name'], app_row['org_name'])
    org = get_organization(app_row['org_id'])
    return render_template(
        'submission_summary.html', app_row=app_row, result=existing, just_submitted=False,
        dimensions=DIMENSIONS, pdf_filename=pdf_filename, benchmarks=get_org_benchmarks(org),
        org_sector_label=_label(SECTORS, org['sector']), org_geo_label=_label(GEOS, org['geo']),
    )


@app.route('/report/<report_token>')
def report(report_token):
    org = get_org_by_report_token(report_token)
    if not org:
        abort(404)

    apps = get_apps_for_org(org['id'])
    rows = []
    for a in apps:
        submission = get_latest_submission(a['id'])
        rows.append({'app': a, 'submission': submission})

    pdf_filename = _pdf_filename(org['name'], 'ConsolidatedReport')
    return render_template(
        'report.html', org=org, rows=rows, dimensions=DIMENSIONS, pdf_filename=pdf_filename,
        benchmarks=get_org_benchmarks(org),
        org_sector_label=_label(SECTORS, org['sector']), org_geo_label=_label(GEOS, org['geo']),
    )


@app.route('/api/health')
def health():
    return {'status': 'ok', 'env': os.getenv('ENV', 'development')}


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5065))
    where = f'http://localhost:{port}' if debug else f'port {port}'
    print(f'\n  omi-deepdive running at {where}')
    if ENV_LOADED:
        print(f'  Config loaded from {os.path.abspath(ENV_PATH)}\n')
    else:
        abs_path = os.path.abspath(ENV_PATH)
        print(f'  No .env found at {abs_path} — using process environment and '
              f'defaults only. Run: cp {abs_path}.example {abs_path}\n')
    app.run(debug=debug, port=port)
