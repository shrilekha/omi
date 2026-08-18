import json
import os
import re
import secrets
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, abort, session
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import (
    init_db, get_app_by_token, get_org_by_report_token, get_apps_for_org,
    get_latest_submission, save_submission, create_organization, create_app,
    get_organization, get_all_organizations, get_app, delete_submissions_for_app,
    delete_submissions_for_org, count_organizations, get_organizations_page,
)
from scoring import compute_scores
from questions import DIMENSIONS, OWNERSHIP_QUESTIONS

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
ADMIN_KEY = os.getenv('ADMIN_KEY', 'changeme-admin-password')

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


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


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

    session['admin'] = True
    session['admin_email'] = email
    return redirect(url_for('admin_new'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('admin_email', None)
    return redirect(url_for('admin_login'))


ORGS_PER_PAGE = 10


@app.route('/admin/new', methods=['GET', 'POST'])
@require_admin
def admin_new():
    if request.method == 'POST':
        org_name = request.form.get('org_name', '').strip()
        if not org_name:
            return render_template('admin_new.html', error='Organization name is required.')

        app_names = [v.strip() for k, v in request.form.items() if k.startswith('app_name_') and v.strip()]
        if not app_names:
            return render_template('admin_new.html', error='At least one app name is required.')

        org_id, _ = create_organization(org_name)
        for name in app_names:
            create_app(org_id, name)

        return redirect(url_for('admin_org', org_id=org_id))

    return render_template('admin_new.html', error=None)


@app.route('/admin/orgs')
@require_admin
def admin_orgs():
    page = max(1, request.args.get('page', 1, type=int))
    total = count_organizations()
    total_pages = max(1, (total + ORGS_PER_PAGE - 1) // ORGS_PER_PAGE)
    page = min(page, total_pages)
    orgs = get_organizations_page(ORGS_PER_PAGE, (page - 1) * ORGS_PER_PAGE)
    return render_template('admin_orgs.html', orgs=orgs, page=page, total_pages=total_pages)


@app.route('/admin/org/<int:org_id>')
@require_admin
def admin_org(org_id):
    org = get_organization(org_id)
    if not org:
        abort(404)
    apps = get_apps_for_org(org_id)
    base_url = request.url_root.rstrip('/')
    return render_template('admin_org.html', org=org, apps=apps, base_url=base_url)


@app.route('/admin/app/<int:app_id>/reset', methods=['POST'])
@require_admin
def admin_reset_app(app_id):
    app_row = get_app(app_id)
    if not app_row:
        abort(404)
    delete_submissions_for_app(app_id)
    return redirect(url_for('admin_org', org_id=app_row['organization_id']))


@app.route('/admin/org/<int:org_id>/reset', methods=['POST'])
@require_admin
def admin_reset_org(org_id):
    org = get_organization(org_id)
    if not org:
        abort(404)
    delete_submissions_for_org(org_id)
    return redirect(url_for('admin_org', org_id=org_id))


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
        return render_template(
            'submission_summary.html', app_row=app_row, result=result, just_submitted=True,
            dimensions=DIMENSIONS, pdf_filename=pdf_filename,
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
    return render_template(
        'submission_summary.html', app_row=app_row, result=existing, just_submitted=False,
        dimensions=DIMENSIONS, pdf_filename=pdf_filename,
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
        'report.html', org=org, rows=rows, dimensions=DIMENSIONS, pdf_filename=pdf_filename
    )


@app.route('/api/health')
def health():
    return {'status': 'ok', 'env': os.getenv('ENV', 'development')}


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5060))
    print(f'\n  omi-deepdive running at http://localhost:{port}\n')
    app.run(debug=debug, port=port)
