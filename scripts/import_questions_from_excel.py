"""
Imports a workbook shaped like the one export_questions_to_excel.py produces back
into frontend/questions.js. Only the 5 data literals (txnVariants, compVariants,
appQuestions, infraQuestions, logQuestions) are touched — everything else in the
file (the header comment block, sectorArchetypeMap, resolveArchetype(),
getSections()) is left byte-for-byte untouched, since questions.js has real logic
in it, not just data.

Reads sheets 'Txn Observability', 'Compliance & Audit', and
'App, Infra & Log (shared)' — the same three the export script builds them from.
Every question lives in exactly one of these three sheets — deliberately no
"everything at once" combined sheet — so there's exactly one place to edit
each question, and no risk of an edit landing in a copy that isn't read here.

All-or-nothing: if any row fails validation, nothing is written — the run prints
every problem it found instead. The same import is also available from the
browser via the "Import from Excel" form on /admin/questions — this script is
for anyone who'd rather script it or run it from a server directly.

Usage:
    python scripts/import_questions_from_excel.py [path/to/workbook.xlsx]

Default path: OMI_Questions_Review.xlsx (project root, export script's own default)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from questions_excel import read_workbook_file, apply_import  # noqa: E402

DEFAULT_XLSX = os.path.join(ROOT, 'OMI_Questions_Review.xlsx')


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XLSX
    if not os.path.exists(path):
        print(f'File not found: {path}')
        sys.exit(1)

    txn, comp, app_q, infra_q, log_q, errors = read_workbook_file(path)

    if errors:
        print(f'{len(errors)} problem(s) found — questions.js was NOT modified:')
        for e in errors:
            print(f'  ! {e}')
        sys.exit(1)

    diff = apply_import(txn, comp, app_q, infra_q, log_q)
    print('Wrote frontend/questions.js (backup at frontend/questions.js.bak)')
    for line in diff:
        print(f'  {line}')


if __name__ == '__main__':
    main()
