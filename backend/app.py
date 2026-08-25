import os
import sys
import requests
from flask import Flask, send_from_directory, request, jsonify
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

from db import init_db, save_submission
from email_sender import send_report_email

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

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
