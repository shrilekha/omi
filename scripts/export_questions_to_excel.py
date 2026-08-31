"""
Exports every OMI assessment question and its answer options (all sector/country
variants) from frontend/questions.js into a single Excel workbook for content review.
The same export is also available from the browser via the "Export to Excel"
button on /admin/questions — this script is for anyone who'd rather script it
or run it from a server directly.

Usage:
    python scripts/export_questions_to_excel.py

Output:
    OMI_Questions_Review.xlsx (project root)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from questions_excel import build_workbook  # noqa: E402

OUTPUT_XLSX = os.path.join(ROOT, 'OMI_Questions_Review.xlsx')


def main():
    wb = build_workbook()
    row_total = sum(ws.max_row - 1 for ws in wb.worksheets)
    wb.save(OUTPUT_XLSX)
    print(f'Wrote {len(wb.worksheets)} sheets ({row_total} rows total) to {OUTPUT_XLSX}')


if __name__ == '__main__':
    main()
