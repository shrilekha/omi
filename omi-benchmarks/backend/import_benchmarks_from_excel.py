"""
Imports a workbook produced by export_benchmarks_to_excel.py (or manually filled in
the same shape) back into the benchmarks table. Safe to re-run: rows are matched by
the table's natural key (metric, sector, geo, revenue_band) and upserted, so importing
the same file twice just updates the same rows again rather than duplicating them.
The same import is also available from the browser via the "Import from Excel" form
on /admin/benchmarks — this script is for anyone who'd rather script it or run it
from a server directly.

Usage:
    python import_benchmarks_from_excel.py [path/to/workbook.xlsx]

Default path: Benchmarks_Export.xlsx (next to this script)
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

from db import init_db
from benchmarks_excel import load_workbook_file, import_workbook

DEFAULT_XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Benchmarks_Export.xlsx')


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XLSX
    if not os.path.exists(path):
        print(f'File not found: {path}')
        sys.exit(1)

    init_db()
    summary = import_workbook(load_workbook_file(path))

    print(f'Inserted: {summary["inserted"]}  Updated: {summary["updated"]}  '
          f'Skipped (blank): {summary["skipped"]}  Errors: {len(summary["errors"])}')
    for e in summary['errors']:
        print(f'  ! {e}')


if __name__ == '__main__':
    main()
