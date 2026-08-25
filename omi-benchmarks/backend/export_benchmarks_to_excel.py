"""
Exports the omi-benchmarks grid — every sector x geo x revenue-band combination,
for every canonical metric — into a single Excel workbook for offline editing.
Run this to produce a fresh copy to hand to the content team, or to re-baseline
after edits have already been imported. The same export is also available from
the browser via the "Export to Excel" button on /admin/benchmarks — this script
is for anyone who'd rather script it or run it from a server directly.

Usage:
    python export_benchmarks_to_excel.py

Output:
    Benchmarks_Export.xlsx (next to this script)
"""
import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

from db import init_db
from benchmarks_excel import build_workbook

OUTPUT_XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Benchmarks_Export.xlsx')


def main():
    init_db()
    wb = build_workbook()
    row_total = sum(ws.max_row - 1 for ws in wb.worksheets)
    wb.save(OUTPUT_XLSX)
    print(f'Wrote {len(wb.worksheets)} metric sheets ({row_total} rows) to {OUTPUT_XLSX}')


if __name__ == '__main__':
    main()
