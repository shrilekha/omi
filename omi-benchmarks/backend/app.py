import os
from functools import wraps
from io import BytesIO

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, send_file
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
    init_db, list_benchmarks, upsert_benchmark, delete_benchmark,
    find_benchmark, find_all_benchmarks,
)
from constants import SECTORS, SECTOR_SHORT_LABELS, GEOS, REVENUE_BANDS, METRICS
from benchmarks_excel import build_workbook, import_workbook, load_workbook_file

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


@app.route('/admin/benchmarks')
@require_admin
def admin_list():
    """The whole sector x geo x revenue-band grid for one capability-area
    metric at a time, pre-populated with every existing value and a blank
    editable row for every combination that doesn't have one yet — filling
    in a cell is just typing a number and tabbing out (see submitCell() in
    admin_list.html), never an "add row" step. Entry is app-agnostic: there
    is no tool selector — a metric here is a canonical capability area read
    by both OMI and omi-deepdive (see constants.py METRICS). Sector/geo/
    revenue filters narrow which combinations are shown; leaving one on its
    default ('') shows every value of that axis, including the 'all
    sectors'-style rollup entries, since those are themselves one of the
    values in each axis's own list."""
    metric = request.args.get('metric') or METRICS[0][0]
    if metric not in dict(METRICS):
        metric = METRICS[0][0]

    sector_filter = request.args.get('sector', '')
    geo_filter = request.args.get('geo', '')
    revenue_filter = request.args.get('revenue_band', '')

    sector_values = [sector_filter] if sector_filter else [s[0] for s in SECTORS]
    geo_values = [geo_filter] if geo_filter else [g[0] for g in GEOS]
    revenue_values = [revenue_filter] if revenue_filter else [r[0] for r in REVENUE_BANDS]

    existing = {
        (r['sector'], r['geo'], r['revenue_band']): r
        for r in list_benchmarks(metric=metric)
    }

    grid_rows = []
    for sector in sector_values:
        for geo in geo_values:
            for revenue_band in revenue_values:
                r = existing.get((sector, geo, revenue_band))
                grid_rows.append({
                    'id': r['id'] if r else '',
                    'sector': sector, 'sector_label': SECTOR_SHORT_LABELS.get(sector, sector),
                    'geo': geo, 'geo_label': dict(GEOS).get(geo, geo),
                    'revenue_band': revenue_band, 'revenue_label': dict(REVENUE_BANDS).get(revenue_band, revenue_band),
                    'benchmark_value': r['benchmark_value'] if r else '',
                    'sample_size': (r['sample_size'] if r and r['sample_size'] is not None else ''),
                    'source': r['source'] if r else '',
                    'effective_date': r['effective_date'] if r else '',
                    'created_by': r['created_by'] if r else '',
                })

    return render_template(
        'admin_list.html', metric=metric, grid_rows=grid_rows, metric_options=METRICS,
        sectors=SECTORS, geos=GEOS, revenue_bands=REVENUE_BANDS,
        sector_filter=sector_filter, geo_filter=geo_filter, revenue_filter=revenue_filter,
        import_result=session.pop('benchmarks_import_result', None),
    )


@app.route('/admin/benchmarks/save', methods=['POST'])
@require_admin
def admin_save():
    """One grid cell's worth of data (see submitCell() in admin_list.html) —
    metric/sector/geo/revenue_band identify WHICH cell; the rest is what got
    typed into it. A blank benchmark value is a no-op (nothing to save yet),
    not an error, since most cells in the grid start out blank on purpose."""
    raw_id = request.form.get('id', '').strip()
    benchmark_id = int(raw_id) if raw_id.isdigit() else None

    value_raw = request.form.get('benchmark_value', '').strip()
    if not value_raw:
        return jsonify({'ok': True, 'id': benchmark_id, 'skipped': True})

    metric = request.form.get('metric', '')
    try:
        benchmark_value = float(value_raw)
    except ValueError:
        benchmark_value = None

    if metric not in dict(METRICS):
        return jsonify({'ok': False, 'error': 'Invalid metric.'}), 422
    if benchmark_value is None or not (0 <= benchmark_value <= 100):
        return jsonify({'ok': False, 'error': 'Benchmark value must be a number between 0 and 100.'}), 422

    sample_size_raw = request.form.get('sample_size', '').strip()
    data = {
        'metric': metric,
        'sector': request.form.get('sector', 'all'),
        'geo': request.form.get('geo', 'all'),
        'revenue_band': request.form.get('revenue_band', 'all'),
        'benchmark_value': benchmark_value,
        'sample_size': int(sample_size_raw) if sample_size_raw.isdigit() else None,
        'source': request.form.get('source', '').strip() or None,
        'effective_date': request.form.get('effective_date', '').strip() or None,
        'created_by': request.form.get('created_by', '').strip() or None,
    }
    try:
        row_id = upsert_benchmark(data, benchmark_id=benchmark_id)
    except Exception as e:
        app.logger.warning(f'upsert_benchmark failed: {e}')
        return jsonify({'ok': False, 'error': 'Could not save (unexpected database error).'}), 422
    return jsonify({'ok': True, 'id': row_id})


@app.route('/admin/benchmarks/<int:benchmark_id>/delete', methods=['POST'])
@require_admin
def admin_delete(benchmark_id):
    delete_benchmark(benchmark_id)
    return jsonify({'ok': True})


@app.route('/admin/benchmarks/export')
@require_admin
def admin_export():
    """Every metric's full sector x geo x revenue-band grid, one sheet per
    metric, as a download — the offline counterpart to typing into the grid
    above. Same shape /admin/benchmarks/import expects back."""
    buf = BytesIO()
    build_workbook().save(buf)
    buf.seek(0)
    return send_file(
        buf, as_attachment=True, download_name='Benchmarks_Export.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


@app.route('/admin/benchmarks/import', methods=['POST'])
@require_admin
def admin_import():
    """Bulk-loads a workbook shaped like the export above. Upserts by natural
    key (metric, sector, geo, revenue_band) — safe to import the same file
    more than once. Results are stashed in the session and shown as a banner
    on the next /admin/benchmarks render (see admin_list())."""
    file = request.files.get('file')
    empty = {'inserted': 0, 'updated': 0, 'skipped': 0, 'errors': []}
    if not file or not file.filename:
        session['benchmarks_import_result'] = {**empty, 'errors': ['No file selected.']}
    else:
        try:
            wb = load_workbook_file(file)
        except Exception:
            session['benchmarks_import_result'] = {
                **empty, 'errors': [f'Could not read "{file.filename}" — is it a valid .xlsx workbook?']
            }
        else:
            session['benchmarks_import_result'] = import_workbook(wb)

    return redirect(url_for('admin_list', metric=request.form.get('metric', '')))


# ─── Read API — server-to-server only, never called from a browser ────────────

@app.route('/api/benchmarks')
@require_api_key
def api_benchmarks():
    sector = request.args.get('sector') or None
    geo = request.args.get('geo') or None
    revenue_band = request.args.get('revenue_band') or None
    metric = request.args.get('metric') or None

    if metric:
        row, matched = find_benchmark(metric, sector, geo, revenue_band)
        if not row:
            return jsonify({'found': False})
        return jsonify({
            'found': True,
            'metric': metric,
            'benchmark_value': row['benchmark_value'],
            'sample_size': row['sample_size'],
            'sector': row['sector'],
            'geo': row['geo'],
            'revenue_band': row['revenue_band'],
            'matched': matched,
        })

    return jsonify(find_all_benchmarks(sector, geo, revenue_band))


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'env': os.getenv('ENV', 'development')})


if __name__ == '__main__':
    init_db()
    debug = os.getenv('ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5070))
    where = f'http://localhost:{port}' if debug else f'port {port}'
    print(f'\n  omi-benchmarks running at {where}')
    if ENV_LOADED:
        print(f'  Config loaded from {os.path.abspath(ENV_PATH)}\n')
    else:
        abs_path = os.path.abspath(ENV_PATH)
        print(f'  No .env found at {abs_path} — using process environment and '
              f'defaults only. Run: cp {abs_path}.example {abs_path}\n')
    app.run(debug=debug, port=port)
