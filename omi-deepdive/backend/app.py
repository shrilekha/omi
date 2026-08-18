import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, abort
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import init_db, get_app_by_token, get_org_by_report_token, get_apps_for_org, get_latest_submission, save_submission
from scoring import compute_scores
from questions import DIMENSIONS, OWNERSHIP_QUESTIONS

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
