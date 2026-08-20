# omi-benchmarks — shared taxonomy
#
# These lists are the canonical vocabulary for sector/geo/revenue band AND
# capability-area metric across ALL THREE apps (OMI, omi-deepdive,
# omi-benchmarks). They are plain data, not shared code — each app is
# deployed independently — so the literal string values below must be kept
# in sync by hand with:
#   - OMI: frontend/questions.js (sectorArchetypeMap) and frontend/index.html
#     (registration sector/country/revenue dropdowns)
#   - omi-deepdive: backend/questions.py (DIMENSIONS ids) and the org-creation
#     sector/geo/revenue fields in admin_new.html
# If you add a sector, geo, revenue band, or metric here, it has no effect on
# either app's own dropdowns — those need the matching edit made separately.

# 'all' is a real stored value, not a null — a benchmark row can be entered
# at any granularity, from fully-specific to a cross-cutting rollup. The API's
# fallback ladder (see db.find_benchmark) relaxes specific axes to 'all' in a
# fixed order when an exact combination has no data.
ALL_SECTORS = 'all'
ALL_GEOS = 'all'
ALL_REVENUE_BANDS = 'all'

# Sector = industry archetype, same grain as OMI's sectorArchetypeMap (the
# archetype, not the raw registration dropdown value — e.g. "Private Sector
# Bank" and "Public Sector Bank" are both bfsi_regulated for benchmarking).
SECTORS = [
    ('all', 'All sectors'),
    ('bfsi_regulated', 'BFSI — Banks, NBFC, Insurance, Capital Markets'),
    ('payments', 'Payments & Financial Infrastructure'),
    ('government', 'Government / PSU'),
    ('technology', 'IT / Technology'),
    ('retail', 'Retail & E-commerce'),
    ('telecom', 'Telecom'),
    ('energy', 'Energy & Utilities'),
    ('manufacturing', 'Manufacturing & Automotive'),
]

# Short forms for the same sectors, used in the dense benchmark grid where
# the full label (above) would blow out the column width. Keep in the same
# order/keys as SECTORS.
SECTOR_SHORT_LABELS = {
    'all': 'All sectors', 'bfsi_regulated': 'BFSI', 'payments': 'Payments',
    'government': 'Government', 'technology': 'Technology', 'retail': 'Retail',
    'telecom': 'Telecom', 'energy': 'Energy', 'manufacturing': 'Manufacturing',
}

# Geo — deliberately coarser than OMI's own registration country dropdown
# (India / Singapore / Middle East / UK / US / Australia / Other). That finer
# breakdown drives *question content* in OMI (Middle East gets a GCC-specific
# regulatory variant, everyone else non-India gets an _intl variant) and is
# worth keeping there, but multiplied through the benchmark grid it's most of
# why a single metric was 360 rows: the customer base is overwhelmingly
# Indian, so a detailed split across a handful of international customers
# isn't worth the entry burden. OMI's backend (OMI_GEO_TO_BENCHMARK_GEO in
# backend/app.py) collapses its own finer country value down to one of these
# before calling this service; omi-deepdive stores directly in this coarser
# vocabulary since its org-creation geo field has no content-selection role.
GEOS = [
    ('all', 'All regions'),
    ('India', 'India'),
    ('Middle East', 'Middle East'),
    ('International', 'International (other)'),
]

# Revenue bands, INR-denominated (₹1 Cr = ₹10 million) since the customer
# base is overwhelmingly Indian — set here rather than behind a USD/INR
# toggle for now; add one later if a meaningful international volume shows
# up. Codes are unchanged from the original USD bands (under_100m etc.) so
# nothing already stored needs to migrate — only the *label* changed.
REVENUE_BANDS = [
    ('all', 'All revenue bands'),
    ('under_100m', '<₹800 Cr'),
    ('100m_1b', '₹800 Cr – ₹8,000 Cr'),
    ('1b_10b', '₹8,000 Cr – ₹80,000 Cr'),
    ('over_10b', '>₹80,000 Cr'),
]

# Metric = a capability area, entered ONCE and read by both OMI and
# omi-deepdive — this list is intentionally app-agnostic; whoever is keying
# in benchmarks shouldn't need to know or care which tool's respondents will
# end up seeing a given number. Each consuming app maps its OWN domain/
# dimension ids onto these canonical ids (see OMI_METRIC_TO_CANONICAL in
# OMI's backend/app.py and DEEPDIVE_METRIC_TO_CANONICAL in omi-deepdive's) —
# some canonical metrics apply to only one app (e.g. `compliance` has no
# omi-deepdive counterpart; `rum`/`synthetic`/`correlation` have no OMI
# counterpart), and that's fine: the app that has no matching domain simply
# never requests that canonical id. `infra_network` deliberately covers BOTH
# of omi-deepdive's separate "Network Layer" and "Infrastructure & Compute"
# dimensions with the same one figure, since OMI treats them as a single
# domain — that's a deliberate coarser reuse, not an oversight.
METRICS = [
    ('overall', 'Overall maturity score'),
    ('txn', 'Business & Transaction Observability'),
    ('app_perf', 'Application Performance'),
    ('infra_network', 'Infrastructure & Network'),
    ('log', 'Log Management'),
    ('compliance', 'Compliance & Audit Readiness'),
    ('rum', 'Real User Monitoring / Digital Experience'),
    ('synthetic', 'Synthetic / Proactive Monitoring'),
    ('correlation', 'Cross-Layer Correlation & Alerting'),
]


def metric_label(metric_id):
    return dict(METRICS).get(metric_id, metric_id)


def sector_label(sector_id):
    return dict(SECTORS).get(sector_id, sector_id)


def sector_short_label(sector_id):
    return SECTOR_SHORT_LABELS.get(sector_id, sector_id)


def geo_label(geo_id):
    return dict(GEOS).get(geo_id, geo_id)


def revenue_band_label(band_id):
    return dict(REVENUE_BANDS).get(band_id, band_id)
