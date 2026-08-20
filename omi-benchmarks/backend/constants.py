# omi-benchmarks — shared taxonomy
#
# These lists are the canonical vocabulary for sector/geo/revenue band across
# ALL THREE apps (OMI, omi-deepdive, omi-benchmarks). They are plain data, not
# shared code — each app is deployed independently — so the literal string
# values below must be kept in sync by hand with:
#   - OMI: frontend/questions.js (sectorArchetypeMap) and frontend/index.html
#     (registration sector/country/revenue dropdowns)
#   - omi-deepdive: backend/questions.py (DIMENSIONS ids) and the org-creation
#     sector/geo/revenue fields in admin_new.html
# If you add a sector, geo, or revenue band here, it has no effect on either
# app's own dropdowns — those need the matching edit made separately.

TOOLS = ['omi', 'deepdive']
TOOL_LABELS = {'omi': 'OMI (self-assessment)', 'deepdive': 'omi-deepdive (per-app)'}

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

# Geo — same values as OMI's registration country dropdown.
GEOS = [
    ('all', 'All regions'),
    ('India', 'India'),
    ('Middle East', 'Middle East'),
    ('Singapore', 'Singapore'),
    ('United Kingdom', 'United Kingdom'),
    ('United States', 'United States'),
    ('Australia', 'Australia'),
    ('Other', 'Other'),
]

REVENUE_BANDS = [
    ('all', 'All revenue bands'),
    ('under_100m', '<$100M'),
    ('100m_1b', '$100M–$1B'),
    ('1b_10b', '$1B–$10B'),
    ('over_10b', '>$10B'),
]

# Metric = domain/dimension id, or 'overall'. Order here is display order.
METRICS = {
    'omi': [
        ('overall', 'Overall maturity score'),
        ('txn', 'Business & Transaction Observability'),
        ('app', 'Application Performance Observability'),
        ('infra', 'Infrastructure & Network Observability'),
        ('log', 'Log Management & Data Lake'),
        ('comp', 'Compliance & Audit Readiness'),
    ],
    'deepdive': [
        ('overall', 'Overall maturity score'),
        ('biztxn', 'Business Transaction / Journey Observability'),
        ('network', 'Network Layer'),
        ('apm', 'Application Performance (APM)'),
        ('infra', 'Infrastructure & Compute'),
        ('rum', 'Real User Monitoring / Digital Experience'),
        ('synthetic', 'Synthetic / Proactive Monitoring'),
        ('correlation', 'Cross-Layer Correlation & Alerting'),
        ('logs', 'Log Observability'),
    ],
}


def metric_label(tool, metric_id):
    for mid, label in METRICS.get(tool, []):
        if mid == metric_id:
            return label
    return metric_id


def sector_label(sector_id):
    return dict(SECTORS).get(sector_id, sector_id)


def geo_label(geo_id):
    return dict(GEOS).get(geo_id, geo_id)


def revenue_band_label(band_id):
    return dict(REVENUE_BANDS).get(band_id, band_id)
