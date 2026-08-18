# omi-deepdive

A per-application end-to-end observability maturity assessment, run independently
with each app owner and coalesced into one consolidated report per organization.

Where OMI assesses an organization's overall observability posture with one
respondent, omi-deepdive assesses **one named application per submission**,
across 8 layers that have to connect for "end-to-end" to mean anything: network,
infrastructure/compute, APM, real-user monitoring (marked N/A where an app has no
direct end-user surface), synthetic/proactive monitoring, business transaction/
journey observability (including whether a durable unique transaction identifier
actually exists and is traceable), cross-layer correlation & alerting, and log
observability.

Every dimension also asks a vendor-neutral question — "what tool, if any, covers
this today" — rather than assuming VuNet. This is a capability audit, not a
VuNet-onboarding survey.

This is a **separate application and database from OMI**. Do not point it at
OMI's production database or hosting — it holds real client tool-stack and
capability-gap data across multiple accounts.

---

## Local setup (under 5 minutes)

**Requirements:** Python 3.9+

```bash
cd omi-deepdive
cp .env.example .env   # defaults are fine for local use

cd backend
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5060**. The SQLite database is auto-created at
`local_dev.db` (project root) on first run.

### Create an organization and its apps

Open `/admin`, sign in (`ADMIN_KEY` password by default, or "Sign in with
Google" once that's configured — see below), create an organization and list
its apps (blank app rows are ignored — 2 apps for one organization, 5 for
another, no fixed count assumed), and the next page shows every link — the
consolidated report link and one link per app, each clickable and openable in
a new tab — ready to copy and send out. `/admin` also lists organizations
created earlier so you can get back to their links at any time.

You get:
- One **per-app link** (`/app/<token>`) to send to each app owner — send each
  owner only their own app's link.
- One **consolidated report link** (`/report/<token>`) — share only with the
  account lead / leadership. It updates automatically as each app owner submits;
  apps with no response yet show as "Not yet submitted" rather than a zero score.

`/admin` is the only page that can create data and isn't protected by an
unguessable token the way `/app/<token>` and `/report/<token>` are — it sits
behind the `ADMIN_KEY` password from `.env` instead. Change that key before any
shared or production use.

### Swapping admin login to Google OAuth

The shared `ADMIN_KEY` password is meant to be temporary. When Google OAuth
credentials are ready, set `GOOGLE_OAUTH_CLIENT_ID` and
`GOOGLE_OAUTH_CLIENT_SECRET` in `.env` (see `.env.example` for where to create
them in Google Cloud Console and which redirect URI to register) and restart
— `/admin` switches to a "Sign in with Google" button and the password form
is retired, no code changes needed. Set `GOOGLE_OAUTH_ALLOWED_DOMAIN` to
restrict sign-in to one Google Workspace domain (checked server-side against
the verified email address, not just requested as a UI hint). Once enabled,
each admin page shows which Google account is signed in.

This is implemented with the Python standard library directly against
Google's OAuth endpoints — enabling it later never requires a new `pip
install`, only the env vars above.

---

## Production setup (Ubuntu VM)

**Requirements:** Python 3.9+, MySQL 8+, its own dedicated database instance.

### 1. Create the database

```sql
CREATE DATABASE omi_deepdive_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'deepdive_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON omi_deepdive_db.* TO 'deepdive_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
mysql -u deepdive_user -p omi_deepdive_db < database/schema.sql
```

### 2. Configure the environment

```bash
cp .env.example .env
```

Edit `.env`: set `ENV=production` and the `DB_*` values above.

### 3. Run with Gunicorn

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5060 app:app
```

Create organizations and apps the same way as in development — via `/admin`
once the app is running (it reads `.env` through the same `db.py` used by the
app, so it writes to the same MySQL database once configured).

Serve behind Nginx with SSL, on its own subdomain/path, and behind an internal
allowlist or VPN if possible. Report and per-app links rely only on their own
unguessable tokens (no login) — an acceptable tradeoff for a short-lived
internal engagement but not a substitute for keeping this off the public
internet if the hosting environment allows restricting it. `/admin` itself is
gated by `ADMIN_KEY` or Google OAuth (see above).

---

## Project structure

```
omi-deepdive/
├── backend/
│   ├── app.py          # Flask app — all routes (assessment, report, admin, OAuth, health)
│   ├── db.py            # DB abstraction (SQLite in dev, MySQL in prod)
│   ├── scoring.py        # Per-dimension + overall scoring, N/A renormalization, maturity band
│   ├── questions.py       # The question bank — edit here to add/reword questions or dimensions
│   ├── templates/
│   │   ├── assess.html          # Per-app assessment form (pre-fills from prior submission)
│   │   ├── submission_summary.html  # Post-submit confirmation and /app/<token>/print view
│   │   ├── report.html          # Consolidated heatmap + per-app detail
│   │   ├── admin_login.html      # Password or Google sign-in
│   │   ├── admin_new.html        # Create-organization tab
│   │   ├── admin_orgs.html       # Existing-organizations tab (paginated)
│   │   └── admin_org.html        # One organization's links + reset actions
│   └── static/style.css
├── database/
│   └── schema.sql        # MySQL schema for production
├── .env.example
└── README.md
```

## Editing the question bank

All question content, dimension weights, and the N/A rule for Real User
Monitoring live in `backend/questions.py`. Weights across all dimensions must
sum to 100 (enforced by an assertion at import time). No other file needs to
change to add, remove, or reword a question — answers are stored as JSON keyed
by question ID, so the database schema doesn't need to change either.

## Maturity bands

Same bands as OMI, for a consistent vocabulary across both tools:

| Score | Band |
|---|---|
| 0–24 | Reactive |
| 25–44 | Aware |
| 45–64 | Structured |
| 65–81 | Proactive |
| 82–100 | Adaptive |

## Dimension weights

| Dimension | Weight |
|---|---|
| Business & Transaction Observability | 25% |
| Network Layer | 15% |
| Application Performance (APM) | 15% |
| Infrastructure & Compute | 10% |
| Real User Monitoring / Digital Experience | 10% |
| Synthetic / Proactive Monitoring | 10% |
| Cross-Layer Correlation & Alerting | 10% |
| Log Observability | 5% |
