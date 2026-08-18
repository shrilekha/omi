import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, abort, session
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import (
    init_db, get_app_by_token, get_org_by_report_token, get_apps_for_org,
    get_latest_submission, save_submission, create_organization, create_app,
    get_organization, get_all_organizations,
)
from scoring import compute_scores
from questions import DIMENSIONS, OWNERSHIP_QUESTIONS

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
ADMIN_KEY = os.getenv('ADMIN_KEY', 'changeme-admin-password')


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('key') == ADMIN_KEY:
            session['admin'] = True
            return redirect(request.args.get('next') or url_for('admin_new'))
        error = 'Incorrect key.'
    return render_template('admin_login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/new', methods=['GET', 'POST'])
@require_admin
def admin_new():
    if request.method == 'POST':
        org_name = request.form.get('org_name', '').strip()
        if not org_name:
            return render_template('admin_new.html', orgs=get_all_organizations(), error='Organization name is required.')

        app_names = [v.strip() for k, v in request.form.items() if k.startswith('app_name_') and v.strip()]
        if not app_names:
            return render_template('admin_new.html', orgs=get_all_organizations(), error='At least one app name is required.')

        org_id, _ = create_organization(org_name)
        for name in app_names:
            create_app(org_id, name)

        return redirect(url_for('admin_org', org_id=org_id))

    return render_template('admin_new.html', orgs=get_all_organizations(), error=None)


@app.route('/admin/org/<int:org_id>')
@require_admin
def admin_org(org_id):
    org = get_organization(org_id)
    if not org:
        abort(404)
    apps = get_apps_for_org(org_id)
    base_url = request.url_root.rstrip('/')
    return render_template('admin_org.html', org=org, apps=apps, base_url=base_url)


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
        return render_template('thanks.html', app_row=app_row, result=result)

    return render_template(
        'assess.html', app_row=app_row, dimensions=DIMENSIONS, ownership=OWNERSHIP_QUESTIONS
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

    return render_template('report.html', org=org, rows=rows, dimensions=DIMENSIONS)


@app.route('/api/health')
def health():
    return {'status': 'ok', 'env': os.getenv('ENV', 'development')}


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5060))
    print(f'\n  omi-deepdive running at http://localhost:{port}\n')
    app.run(debug=debug, port=port)
