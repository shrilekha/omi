# omi-benchmarks

Industry benchmark reference data — leadership/customer success key in peer
maturity figures here, and both **OMI** and **omi-deepdive** read them
server-to-server to show "how do we compare to peers like us" alongside a
respondent's own score.

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
- Both are reading the *same* underlying data, entered once, here.

## The data model

One table, `benchmarks`. Each row is one metric's peer figure for one peer
group:

| Column | Meaning |
|---|---|
| `tool` | `omi` or `deepdive` — the two apps' domain/dimension taxonomies don't line up (OMI has 5 domains, deepdive has 8 dimensions), so a benchmark belongs to exactly one |
| `metric` | a domain/dimension id for that tool, or `overall` |
| `sector` | an industry archetype id, or `all` |
| `geo` | a country/region, or `all` |
| `revenue_band` | a revenue band id, or `all` |
| `median_score` | 0–100 |
| `sample_size`, `source`, `effective_date`, `created_by` | optional context |

`all` is a real stored value, not a null — you can enter a row at any
granularity, from fully specific (BFSI, India, $1B–$10B) to a broad rollup
(all sectors, all geos, all revenue bands = the global average for that
metric). **`(tool, metric, sector, geo, revenue_band)` is unique** — there's
exactly one row for any given combination.

### How a lookup resolves — read this before assuming a query "has no data"

`find_benchmark()` (in `backend/db.py`) tries the caller's exact
sector/geo/revenue combination first, then relaxes axes **in this fixed
order** when the exact combination isn't stored: drop revenue band → drop
geo → drop sector (down to the fully global row). It returns which axes
actually held after relaxation, so a caller can be honest about what's being
shown ("peers in Banking" rather than silently claiming "peers in Banking,
India, $1B–$10B" once revenue or geo had to give).

This is deliberately *not* a live aggregation across whatever rows happen to
exist — it's a fixed lookup-with-fallback across rows someone entered on
purpose (including entering the rollup rows explicitly). Sparser data means
more fallback hits, not wrong math, but the rollup rows still need to
actually be entered — nothing computes them for you.

## Local setup

```bash
cd omi-benchmarks
cp .env.example .env
cd backend
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5070** (redirects to `/admin`). SQLite DB
auto-created at `local_dev.db` (project root) on first run.

## Admin UI

`/admin` is gated by a single shared `ADMIN_KEY` from `.env` — same
password-only tradeoff OMI and omi-deepdive both started with (no per-user
identity; anyone with the key has full access). `/admin/benchmarks` lists
every row with tool/sector filters; **+ Add benchmark** opens a form (tool →
metric → sector → geo → revenue band → median score, plus optional sample
size / source / effective date / entered by). The metric dropdown is scoped
to whichever tool you pick.

## Read API — for OMI's and omi-deepdive's backends only

```
GET /api/benchmarks?tool=omi&sector=bfsi_regulated&geo=India&revenue_band=1b_10b
```

Header: `X-Api-Key: <BENCHMARKS_API_KEY>`. Omit `sector`/`geo`/`revenue_band`
to mean "don't filter on this axis" (equivalent to `all`). Omit `metric` to
get every metric for that tool in one response — this is what a report
screen wants, one call covering every domain/dimension at once:

```json
{
  "txn": {"median_score": 61.5, "sample_size": 14, "sector": "bfsi_regulated", "geo": "India", "revenue_band": "1b_10b", "matched": {"sector_matched": true, "geo_matched": true, "revenue_matched": true}},
  "app": {"median_score": 58.0, "sample_size": 9, "sector": "bfsi_regulated", "geo": "all", "revenue_band": "all", "matched": {"sector_matched": true, "geo_matched": false, "revenue_matched": false}}
}
```

Pass `metric=txn` for a single metric — returns `{"found": false}` if
nothing matched even after every fallback.

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
bands, and per-tool metrics — but it's **plain data, not shared code**: OMI
and omi-deepdive each have their own copies of the sector/geo/revenue
options in their own registration/org-creation forms. If you add a sector,
geo, revenue band, or (for OMI) a domain here, it does not automatically
appear anywhere else — update the matching list in whichever app(s) need it,
by hand, to keep the three in sync. See the comment at the top of
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
│   ├── app.py          # Flask app — admin auth, CRUD, the read API, health
│   ├── db.py            # DB abstraction + find_benchmark() fallback ladder
│   ├── constants.py      # Canonical tool/metric/sector/geo/revenue-band lists
│   ├── templates/
│   │   ├── admin_login.html
│   │   ├── admin_list.html
│   │   └── admin_form.html
│   └── static/style.css
├── database/
│   └── schema.sql        # MySQL schema for production
├── .env.example
└── README.md
```
