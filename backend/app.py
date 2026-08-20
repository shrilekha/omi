import os
import sys
import requests
from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import init_db, save_submission
from email_sender import send_report_email

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# omi-benchmarks is a separate service (see ../omi-benchmarks). This backend
# proxies to it server-to-server so the shared API key never reaches the
# browser, and so the browser only ever talks to same-origin /api/*.
BENCHMARKS_URL = os.getenv('BENCHMARKS_URL', '').rstrip('/')
BENCHMARKS_API_KEY = os.getenv('BENCHMARKS_API_KEY', '')


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

    params = {'tool': 'omi'}
    for key in ('sector', 'geo', 'revenue_band'):
        value = request.args.get(key, '')
        if value:
            params[key] = value

    try:
        resp = requests.get(
            f'{BENCHMARKS_URL}/api/benchmarks', params=params,
            headers={'X-Api-Key': BENCHMARKS_API_KEY}, timeout=5,
        )
        return jsonify(resp.json()), resp.status_code
    except (requests.RequestException, ValueError) as e:
        app.logger.warning(f'benchmarks proxy error: {e}')
        return jsonify({})


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'env': os.getenv('ENV', 'development')})


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5050))
    print(f'\n  OMI running at http://localhost:{port}\n')
    app.run(debug=debug, port=port)
