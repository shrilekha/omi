"""Seed an organization and its apps, and print the tokenized links to hand out.

Usage:
    cd omi-deepdive/backend
    python seed.py "IndusInd Bank" "Mobile Banking App" "Internet Banking Portal" \
        "UPI Payments Service" "Loan Origination System" "Trade Finance Platform"

The first argument is the organization name; every argument after it becomes one
app under that organization. Run with ENV unset (or ENV=development) to seed the
local SQLite database used by `python app.py`; set ENV=production (with the DB_*
vars from .env) to seed the production MySQL database instead.
"""
import os
import sys

from db import init_db, create_organization, create_app

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5060')


def main():
    if len(sys.argv) < 3:
        print('Usage: python seed.py "<Organization Name>" "<App 1>" ["<App 2>" ...]')
        sys.exit(1)

    org_name = sys.argv[1]
    app_names = sys.argv[2:]

    init_db()

    org_id, report_token = create_organization(org_name)
    print(f'\nOrganization: {org_name} (id={org_id})')
    print(f'Consolidated report link (share only with the account lead / leadership):')
    print(f'  {BASE_URL}/report/{report_token}\n')

    print('Per-app interview links (send one to each app owner):')
    for name in app_names:
        _, token = create_app(org_id, name)
        print(f'  {name:<40} {BASE_URL}/app/{token}')
    print()


if __name__ == '__main__':
    main()
