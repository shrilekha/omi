# omi-benchmarks

Industry benchmark reference data — leadership/customer success key in peer
maturity figures here, **once, app-agnostically**, and both **OMI** and
**omi-deepdive** read them server-to-server to show "how do we compare to
peers like us" alongside a respondent's own score.

This is a **separate application and database** from both OMI and
omi-deepdive, same as those two are separate from each other. It holds
anonymized, aggregate figures — not any single client's raw response data —
but it's still a distinct service so either of the other two apps can go
down without taking benchmark data with it, and vice versa.

---

## Why this exists

- OMI's report can show a respondent how their score compares to peers —
  filtered by industry, region, and/or revenue band, in any combination the
  respondent picks.
- omi-deepdive's per-app and consolidated reports show the same kind of
  comparison, but with no picker — the organization's sector/geo/revenue
  (set once, at org creation) fixes which peer group is shown.
- Both are reading the *same* underlying data, entered once, here — whoever
  keys in a figure doesn't need to know or care which tool's respondents
  will eventually see it.

## The data model

One table, `benchmarks`. Each row is one capability area's peer figure for
one peer group:

| Column | Meaning |
|---|---|
| `metric` | a canonical capability-area id, or `overall` — see `backend/constants.py` `METRICS`. Deliberately **not** tied to either app's own domain/dimension ids; each app maps its own onto these (see "App-agnostic metrics" below) |
| `sector` | an industry archetype id, or `all` |
| `geo` | a country/region, or `all` |
| `revenue_band` | a revenue band id, or `all` |
| `benchmark_value` | 0–100 — the peer figure itself |
| `sample_size`, `source`, `effective_date`, `created_by` | optional context |

`all` is a real stored value, not a null — you can enter a row at any
granularity, from fully specific (BFSI, India, ₹8,000 Cr–₹80,000 Cr) to a broad rollup
(all sectors, all geos, all revenue bands = the global figure for that
metric). **`(metric, sector, geo, revenue_band)` is unique** — there's
exactly one row for any given combination.

### App-agnostic metrics — why there's no "tool" column

OMI has 5 domains; omi-deepdive has 8 dimensions; they don't line up
one-to-one. Rather than making whoever enters benchmarks pick a tool first
and duplicate figures across both, this table stores against **one shared
canonical list** (`METRICS` in `backend/constants.py`), and each consuming
app translates:

| Canonical metric | OMI domain | omi-deepdive dimension |
|---|---|---|
| `overall` | `overall` | `overall` |
| `txn` | `txn` | `biztxn` |
| `app_perf` | `app` | `apm` |
| `infra_network` | `infra` | `infra` **and** `network` (both read the *same* figure — OMI treats them as one domain, deepdive splits it into two) |
| `log` | `log` | `logs` |
| `compliance` | `comp` | *(none — omi-deepdive has no compliance dimension)* |
| `rum` | *(none — OMI has no RUM domain)* | `rum` |
| `synthetic` | *(none)* | `synthetic` |
| `correlation` | *(none)* | `correlation` |

The translation dicts (`OMI_METRIC_TO_CANONICAL` in OMI's `backend/app.py`,
`DEEPDIVE_METRIC_TO_CANONICAL` in omi-deepdive's) live in each *consuming*
app, not here — this service stays domain-agnostic on purpose.

### How a lookup resolves — read this before assuming a query "has no data"

`find_benchmark()` (in `backend/db.py`) tries the caller's exact
sector/geo/revenue combination first, then relaxes axes **in this fixed
order** when the exact combination isn't stored: drop revenue band → drop
geo → drop sector (down to the fully global row). It returns which axes
actually held after relaxation, so a caller can be honest about what's being
shown ("peers in Banking" rather than silently claiming "peers in Banking,
India, ₹8,000 Cr–₹80,000 Cr" once revenue or geo had to give).

This is deliberately *not* a live aggregation across whatever rows happen to
exist — it's a fixed lookup-with-fallback across rows someone entered on
purpose (including entering the rollup rows explicitly). Sparser data means
more fallback hits, not wrong math, but the rollup rows still need to
actually be entered — nothing computes them for you.

## Local setup

To run this alongside OMI and omi-deepdive with one command instead, see
`python start_all.py` in the [root README](../README.md#quick-start--run-all-three-at-once).

```bash
cd omi-benchmarks
cp .env.example .env
cd backend
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5070** (redirects to `/admin`). SQLite DB
auto-created at `local_dev.db` (project root) on first run.

## Admin UI — a pre-populated grid, not an "add row" form

`/admin` is gated by a single shared `ADMIN_KEY` from `.env` — same
password-only tradeoff OMI and omi-deepdive both started with (no per-user
identity; anyone with the key has full access).

`/admin/benchmarks` shows the **entire sector × geo × revenue-band grid**
for one metric at a time (pick it from the dropdown — up to 180 rows: 9
sectors × 4 geos × 5 revenue bands), already populated with every existing
value; the rest are blank editable rows, not something you "add." Type a
benchmark value into a cell and tab out — it saves itself (debounced so
filling in several fields on one row is one request, not several).
Sector/geo/revenue filters narrow which rows are shown; they're a
convenience, not a gate. A small **×** on a filled row clears it (deletes
the record).

The geo axis (India / Middle East / International) is deliberately coarser
than OMI's own country dropdown, and revenue bands are INR-denominated
(₹ Crore) — both because the customer base is overwhelmingly Indian and a
finer international split isn't worth the entry burden it would add. See
the comments on `GEOS`/`REVENUE_BANDS` in `backend/constants.py` if that
balance ever needs to change.

A save that's still pending when you navigate away (e.g. straight to Log
out) is flushed immediately via `beforeunload`/`pagehide`, and the request
itself uses `fetch(..., {keepalive: true})` so it can finish even mid
page-unload — without both of those, a value typed right before navigating
away could be silently lost.

## Read API — for OMI's and omi-deepdive's backends only

```
GET /api/benchmarks?sector=bfsi_regulated&geo=India&revenue_band=1b_10b
```

Header: `X-Api-Key: <BENCHMARKS_API_KEY>`. Omit `sector`/`geo`/`revenue_band`
to mean "don't filter on this axis" (equivalent to `all`). Omit `metric` to
get every canonical metric in one response — this is what a report screen
wants, one call covering every domain/dimension at once:

```json
{
  "txn": {"benchmark_value": 61.5, "sample_size": 14, "sector": "bfsi_regulated", "geo": "India", "revenue_band": "1b_10b", "matched": {"sector_matched": true, "geo_matched": true, "revenue_matched": true}},
  "app_perf": {"benchmark_value": 58.0, "sample_size": 9, "sector": "bfsi_regulated", "geo": "all", "revenue_band": "all", "matched": {"sector_matched": true, "geo_matched": false, "revenue_matched": false}}
}
```

Pass `metric=txn` for a single metric — returns `{"found": false}` if
nothing matched even after every fallback. The keys in an all-metrics
response are always the **canonical** ids above — callers translate them
to their own domain/dimension ids themselves (see "App-agnostic metrics").

This endpoint is **never** called from either app's browser-facing pages —
each app's own backend calls it server-side and relays only what it needs to
the browser, so `BENCHMARKS_API_KEY` never reaches a client.

## Production deployment

Same pattern as OMI and omi-deepdive:

```sql
CREATE DATABASE omi_benchmarks_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'benchmarks_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON omi_benchmarks_db.* TO 'benchmarks_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
mysql -u benchmarks_user -p omi_benchmarks_db < database/schema.sql
```

Set `ENV=production`, the `DB_*` values, a real `SECRET_KEY`, `ADMIN_KEY`,
and `BENCHMARKS_API_KEY` in `.env`, then:

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5070 app:app
```

Put this behind an internal allowlist/VPN if the hosting environment allows
it — there's no reason for `/admin` or `/api/benchmarks` to be reachable
from the open internet at all; only OMI's and omi-deepdive's backend hosts
need network access to it.

## Keeping the taxonomy in sync

`backend/constants.py` is the canonical list of sectors, geos, revenue
bands, and metrics — but it's **plain data, not shared code**: OMI and
omi-deepdive each have their own copies of the sector/geo/revenue options in
their own registration/org-creation forms, and their own metric→canonical
translation dicts (see "App-agnostic metrics" above). If you add a sector,
geo, revenue band, or metric here, it does not automatically appear or get
used anywhere else — update the matching list/dict in whichever app(s) need
it, by hand, to keep everything in sync. See the comment at the top of
`constants.py` for exactly where each app's copy lives.

## Seeding

This is empty on first deploy. Nothing in either OMI or omi-deepdive shows a
peer comparison until someone — leadership or customer success — has keyed
in enough rows here to cover the sector × geo × revenue-band combinations
those tools' respondents actually fall into. That's a real one-time (and
ongoing) data-entry task, not something the plumbing does for you.

## Project structure

```
omi-benchmarks/
├── backend/
│   ├── app.py          # Flask app — admin auth, the grid CRUD, the read API, health
│   ├── db.py            # DB abstraction + find_benchmark() fallback ladder
│   ├── constants.py      # Canonical metric/sector/geo/revenue-band lists
│   ├── templates/
│   │   ├── admin_login.html
│   │   └── admin_list.html   # the grid — this is the only authenticated page
│   └── static/style.css
├── database/
│   └── schema.sql        # MySQL schema for production
├── .env.example
└── README.md
```
