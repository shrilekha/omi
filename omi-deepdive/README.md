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

## Access model — three distinct concepts

It matters that these three never get conflated, since they answer different
questions and are enforced completely independently in the code:

| Concept | Answers | Mechanism |
|---|---|---|
| **Identity** | Who are you? | Google OAuth (or nothing at all — the `ADMIN_KEY` password has no per-user identity) |
| **Authorization** | What are you allowed to do internally? | `admin_users` table — a role (`admin`, `assessment_manager`, `reviewer`, `executive`) |
| **External respondent access** | Can this one link fill in this one app's assessment? | The per-app `access_token` in the URL — no login, no role, and it cannot reach any `/admin` or `/dashboard` route no matter what |

A Google account being a real, verified identity is **necessary but not
sufficient** to get into this tool — it must also carry a role. And no matter
how someone got hold of an `/app/<token>` link, that token can only ever open
that one app's assessment form; it has no path to `/admin`, `/dashboard`, or
any other app's data.

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

Open **http://localhost:5060** (it redirects straight to `/admin`). The SQLite
database — including the `admin_users` RBAC table — is auto-created at
`local_dev.db` (project root) on first run; no separate migration step in dev.

### Create an organization and its apps

Sign in at `/admin` (password by default, or "Sign in with Google" — see
below), create an organization and list its apps (blank app rows are ignored —
2 apps for one organization, 5 for another, no fixed count assumed), and the
next page shows every link — the consolidated report link and one link per
app, each clickable and openable in a new tab — ready to copy and send out.
`/admin` also lists organizations created earlier so you can get back to their
links at any time.

You get:
- One **per-app link** (`/app/<token>`) to send to each app owner — send each
  owner only their own app's link. They can revisit it any time to revise and
  resubmit; the newest submission is what shows in the report.
- One **consolidated report link** (`/report/<token>`) — share only with the
  account lead / leadership. It updates automatically as each app owner submits;
  apps with no response yet show as "Not yet submitted" rather than a zero score.

Both links rely solely on their own long, unguessable token — no login, no
expiry, no revocation beyond the admin's **Reset** action (which deletes the
stored response but keeps the same link working). That's a deliberate
tradeoff for a short-lived internal engagement: simple to hand out and use,
at the cost of relying on the token staying secret rather than a real
access-control check. Don't treat these links as fit for indefinite reuse
across unrelated engagements — start a fresh organization instead.

---

## Admin access & RBAC

### Password mode (default)

Out of the box, `/admin` is gated by a single shared `ADMIN_KEY` from `.env`.
Anyone with the key has full access to everything — there's no per-user
identity to check a role against, so `require_role()` in `app.py` simply
falls back to "logged in = full access" in this mode, same as before RBAC
existed. This is fine for a single person or a small trusted team getting
started, and it's *not* fine as a long-lived setup for a team with any
turnover, since revoking access means changing a password everyone shares.

### Switching to Google OAuth + RBAC

Set both `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in `.env`
and restart. This is a **swap**, not an additional option: the password form
is retired (`POST /admin` 404s) and `/admin` shows a "Sign in with Google"
button instead. It's implemented with the Python standard library directly
against Google's OAuth endpoints — no Authlib/google-auth dependency, so
enabling this later never requires a new `pip install`, only the env vars
below and a registered redirect URI.

**Setup:**
1. [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials)
   → Create Credentials → OAuth client ID → Application type: **Web application**.
2. Authorized redirect URI — must be **exactly**:
   `<your-deployed-base-url>/admin/google/callback`
   (e.g. `https://omi-deepdive.yourdomain.com/admin/google/callback`). See
   the proxy note below — this is the single most common setup failure.
3. Paste the generated client ID/secret into `.env` as `GOOGLE_OAUTH_CLIENT_ID`
   / `GOOGLE_OAUTH_CLIENT_SECRET`, restart.
4. Optionally set `GOOGLE_OAUTH_ALLOWED_DOMAIN` (e.g. `vunetsystems.com`) to
   reject sign-in from outside your Workspace domain — checked server-side
   against Google's verified email response, not just requested as a UI hint.

**Roles** (`admin_users` table): `admin`, `assessment_manager`, `reviewer`,
`executive`. Current enforcement:

| Route | Allowed roles |
|---|---|
| `/admin/new`, `/admin/orgs`, `/admin/org/<id>`, reset actions | `admin`, `assessment_manager` |
| `/admin/users` (manage roles) | `admin` only |
| `/dashboard` (read-only org list → report links) | `admin`, `assessment_manager`, `reviewer`, `executive` |
| `/app/<token>`, `/report/<token>` | none of the above apply — these are external, token-only, see above |

**Bootstrapping the first admin:** `admin_users` starts empty, so nothing
above could ever grant itself access. Set `INITIAL_ADMIN_EMAILS` in `.env` to
a comma-separated list of Google emails — the first time one of them signs
in, it's automatically granted the `admin` role and gets a real row in
`admin_users`. It's safe to leave this set permanently; it only ever creates
a row if one doesn't already exist, never overrides an existing one. From
then on, manage everyone (including changing your own role, carefully) from
**Manage users** (`/admin/users`, linked from every admin page when
signed in as `admin`).

**Deactivating someone**: use `/admin/users` → Deactivate. Note this doesn't
force out an already-open browser session immediately — Flask sessions here
are signed cookies with no server-side session store, so someone already
signed in stays signed in until they log out or their session cookie expires.
For urgent revocation, rotating `SECRET_KEY` invalidates *every* active
session at once (a blunt instrument — it logs everyone out, not just one
person).

---

## Production deployment

**Requirements:** Python 3.9+, MySQL 8+, its own dedicated database instance.

### 1. Database

```sql
CREATE DATABASE omi_deepdive_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'deepdive_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON omi_deepdive_db.* TO 'deepdive_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
mysql -u deepdive_user -p omi_deepdive_db < database/schema.sql
```

`schema.sql` includes `admin_users` — no separate migration needed even if
you plan to turn on OAuth/RBAC later rather than immediately.

### 2. Configure the environment

```bash
cp .env.example .env
```

Edit `.env`: set `ENV=production`, the `DB_*` values above, a real random
`SECRET_KEY` (`python -c "import secrets; print(secrets.token_hex(32))"`),
and — if using OAuth — the `GOOGLE_OAUTH_*` / `INITIAL_ADMIN_EMAILS` values
from the section above.

### 3. Run with Gunicorn

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5060 app:app
```

Multiple workers are fine with no extra configuration: sessions are stateless
signed cookies (no server-side session store to keep in sync), and each
worker reads the same `.env` at startup.

### 4. Serve behind Nginx with SSL

Put this on its own subdomain/path, and behind an internal allowlist or VPN
if the hosting environment allows it — the per-app and report links rely only
on their own unguessable tokens (deliberately no login for those, see the
access model above), which is an acceptable tradeoff for a short-lived
internal engagement but not a substitute for keeping this off the open
internet where that's an option.

Minimal reverse-proxy config (adjust paths/domain):

```nginx
server {
    listen 443 ssl;
    server_name omi-deepdive.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5060;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Proxy considerations — read this before enabling Google OAuth in production

`app.py` wires in Werkzeug's `ProxyFix`, which trusts those `X-Forwarded-*`
headers to reconstruct the real scheme/host/port a browser is actually using
— that's what makes the links shown on `/admin/org/<id>` correct instead of
showing `localhost` or an internal container hostname (this exact problem
showed up during development behind a Codespaces forwarded URL; ProxyFix is
the fix and it generalizes to any reverse proxy, Nginx included).

This matters even more with Google OAuth than it did before: the redirect URI
Flask builds (`url_for('admin_google_callback', _external=True)`) **must
match, character for character**, the redirect URI registered in Google Cloud
Console. If the proxy headers above aren't forwarded correctly, Flask will
compute the wrong scheme or host, Google will refuse with
`redirect_uri_mismatch`, and sign-in will fail before it ever reaches this
app's code. If that happens: check the Nginx config above is actually in
effect, and confirm `https` (not `http`) is what's arriving in
`X-Forwarded-Proto`.

Google also requires an **HTTPS** redirect URI for any real deployment —
`http://localhost:...` is allowed for local testing only.

---

## Known limitations

- **Per-app/report links don't expire and can't be individually revoked** —
  only reset (clears the response, same link keeps working). Treat the token
  as the only thing protecting that link, and start a fresh organization for
  a new engagement rather than reusing old links.
- **Deactivating an admin user doesn't end their current session** — see
  the RBAC section above. There's no server-side session store to revoke
  from; rotating `SECRET_KEY` is the blunt-force option if that's ever urgent.
- **No audit log** of who created/reset what beyond what's visible live in
  the admin UI (which app owner submitted, when). If per-action history
  becomes a real requirement, that's a natural next addition rather than
  something implicit today.
- **Password mode has no per-user identity at all** — anyone with `ADMIN_KEY`
  is indistinguishable from anyone else with it. This is exactly what Google
  OAuth + RBAC (above) replaces.

---

## Project structure

```
omi-deepdive/
├── backend/
│   ├── app.py          # Flask app — all routes (assessment, report, admin, OAuth, RBAC, health)
│   ├── db.py            # DB abstraction (SQLite in dev, MySQL in prod)
│   ├── scoring.py        # Per-dimension + overall scoring, N/A renormalization, maturity band
│   ├── questions.py       # The question bank — edit here to add/reword questions or dimensions
│   ├── templates/
│   │   ├── assess.html          # Per-app assessment form (pre-fills from prior submission)
│   │   ├── submission_summary.html  # Post-submit confirmation and /app/<token>/print view
│   │   ├── report.html          # Consolidated heatmap + per-app detail
│   │   ├── dashboard.html        # Read-only org list for reviewer/executive/etc.
│   │   ├── admin_login.html      # Password or Google sign-in
│   │   ├── admin_forbidden.html   # Shown when a role can't reach a route it tried
│   │   ├── admin_users.html      # Manage admin_users (admin-only)
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
