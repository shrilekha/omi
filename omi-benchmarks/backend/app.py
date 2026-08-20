import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from db import (
    init_db, list_benchmarks, get_benchmark, upsert_benchmark, delete_benchmark,
    find_benchmark, find_benchmarks_for_tool,
)
from constants import TOOLS, TOOL_LABELS, SECTORS, GEOS, REVENUE_BANDS, METRICS

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

ADMIN_KEY = os.getenv('ADMIN_KEY', 'changeme-admin-password')
# Shared secret for the server-to-server read API (OMI / omi-deepdive backends
# only — this is never called from a browser). Leaving it unset in dev is fine;
# it must be set in production or every /api/benchmarks call 401s.
API_KEY = os.getenv('BENCHMARKS_API_KEY', '')


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if API_KEY and request.headers.get('X-Api-Key') != API_KEY:
            abort(401)
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    return redirect(url_for('admin_login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET' and session.get('admin'):
        return redirect(url_for('admin_list'))
    error = None
    if request.method == 'POST':
        if request.form.get('key') == ADMIN_KEY:
            session['admin'] = True
            return redirect(request.args.get('next') or url_for('admin_list'))
        error = 'Incorrect key.'
    return render_template('admin_login.html', error=error)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


def _decorate(row):
    """Add the display labels _row_pair.html needs, without mutating the DB row dict in place."""
    row = dict(row)
    row['metric_label'] = dict(METRICS.get(row['tool'], [])).get(row['metric'], row['metric'])
    row['sector_label'] = dict(SECTORS).get(row['sector'], row['sector'])
    row['geo_label'] = dict(GEOS).get(row['geo'], row['geo'])
    row['revenue_label'] = dict(REVENUE_BANDS).get(row['revenue_band'], row['revenue_band'])
    return row


_BLANK_ROW = {
    'id': 'new', 'tool': '', 'metric': '', 'sector': 'all', 'geo': 'all', 'revenue_band': 'all',
    'median_score': None, 'sample_size': None, 'source': None, 'effective_date': None, 'created_by': None,
}

_ROW_TEMPLATE_CTX = dict(tools=TOOLS, tool_labels=TOOL_LABELS, sectors=SECTORS, geos=GEOS,
                          revenue_bands=REVENUE_BANDS, metrics_by_tool=METRICS)


@app.route('/admin/benchmarks')
@require_admin
def admin_list():
    tool = request.args.get('tool') or None
    sector = request.args.get('sector') or None
    rows = [_decorate(r) for r in list_benchmarks(tool=tool, sector=sector)]
    return render_template(
        'admin_list.html', rows=rows, blank_row=_BLANK_ROW, error=None, edit_only=False,
        selected_tool=tool, selected_sector=sector, **_ROW_TEMPLATE_CTX,
    )


@app.route('/admin/benchmarks/save', methods=['POST'])
@require_admin
def admin_save():
    """Inline-editor endpoint (see admin_list.html / _row_pair.html) — adds or
    updates one row and returns the rendered row-pair HTML fragment to swap
    into the table via fetch(), so the page never fully reloads. On a
    validation error, returns just the editor with the error and the
    submitted values preserved, instead of the saved row."""
    raw_id = request.form.get('id', '').strip()
    benchmark_id = int(raw_id) if raw_id.isdigit() else None

    tool = request.form.get('tool', '')
    metric = request.form.get('metric', '')
    valid_metrics = dict(METRICS.get(tool, []))
    try:
        median_score = float(request.form.get('median_score', ''))
    except ValueError:
        median_score = None

    error = None
    if tool not in TOOLS:
        error = 'Choose a valid tool.'
    elif metric not in valid_metrics:
        error = 'Choose a metric that belongs to the selected tool.'
    elif median_score is None or not (0 <= median_score <= 100):
        error = 'Median score must be a number between 0 and 100.'

    if not error:
        sample_size_raw = request.form.get('sample_size', '').strip()
        data = {
            'tool': tool,
            'metric': metric,
            'sector': request.form.get('sector', 'all'),
            'geo': request.form.get('geo', 'all'),
            'revenue_band': request.form.get('revenue_band', 'all'),
            'median_score': median_score,
            'sample_size': int(sample_size_raw) if sample_size_raw.isdigit() else None,
            'source': request.form.get('source', '').strip() or None,
            'effective_date': request.form.get('effective_date', '').strip() or None,
            'created_by': request.form.get('created_by', '').strip() or None,
        }
        try:
            row_id = upsert_benchmark(data, benchmark_id=benchmark_id)
            row = _decorate(get_benchmark(row_id))
            return render_template('_row_pair.html', row=row, error=None, edit_only=False, **_ROW_TEMPLATE_CTX)
        except Exception as e:
            # Most likely the UNIQUE(tool, metric, sector, geo, revenue_band)
            # constraint — that exact peer-group combination already has a row.
            error = ('A benchmark for this exact tool/metric/sector/geo/revenue '
                      'combination already exists — edit that row instead.')
            app.logger.warning(f'upsert_benchmark failed: {e}')

    row = request.form.to_dict()
    row['id'] = benchmark_id if benchmark_id else 'new'
    return render_template('_row_pair.html', row=row, error=error, edit_only=True, **_ROW_TEMPLATE_CTX), 422


@app.route('/admin/benchmarks/<int:benchmark_id>/delete', methods=['POST'])
@require_admin
def admin_delete(benchmark_id):
    delete_benchmark(benchmark_id)
    return ('', 204)


# ─── Read API — server-to-server only, never called from a browser ────────────

@app.route('/api/benchmarks')
@require_api_key
def api_benchmarks():
    tool = request.args.get('tool', '')
    if tool not in TOOLS:
        return jsonify({'error': f'tool must be one of {TOOLS}'}), 400

    sector = request.args.get('sector') or None
    geo = request.args.get('geo') or None
    revenue_band = request.args.get('revenue_band') or None
    metric = request.args.get('metric') or None

    if metric:
        row, matched = find_benchmark(tool, metric, sector, geo, revenue_band)
        if not row:
            return jsonify({'found': False})
        return jsonify({
            'found': True,
            'metric': metric,
            'median_score': row['median_score'],
            'sample_size': row['sample_size'],
            'sector': row['sector'],
            'geo': row['geo'],
            'revenue_band': row['revenue_band'],
            'matched': matched,
        })

    return jsonify(find_benchmarks_for_tool(tool, sector, geo, revenue_band))


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'env': os.getenv('ENV', 'development')})


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5070))
    print(f'\n  omi-benchmarks running at http://localhost:{port}\n')
    app.run(debug=debug, port=port)
