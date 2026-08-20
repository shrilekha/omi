# omi-deepdive — sector/geo/revenue-band taxonomy for organizations
#
# Same literal values as omi-benchmarks/backend/constants.py and OMI's own
# registration dropdowns — plain data, not shared code (each app deploys
# independently), so keep these three copies in sync by hand. This is what
# lets an org created here be matched against the right row in the separate
# omi-benchmarks service without any translation step.

SECTORS = [
    ('all', 'Not specified'),
    ('bfsi_regulated', 'BFSI — Banks, NBFC, Insurance, Capital Markets'),
    ('payments', 'Payments & Financial Infrastructure'),
    ('government', 'Government / PSU'),
    ('technology', 'IT / Technology'),
    ('retail', 'Retail & E-commerce'),
    ('telecom', 'Telecom'),
    ('energy', 'Energy & Utilities'),
    ('manufacturing', 'Manufacturing & Automotive'),
]

GEOS = [
    ('all', 'Not specified'),
    ('India', 'India'),
    ('Middle East', 'Middle East'),
    ('Singapore', 'Singapore'),
    ('United Kingdom', 'United Kingdom'),
    ('United States', 'United States'),
    ('Australia', 'Australia'),
    ('Other', 'Other'),
]

REVENUE_BANDS = [
    ('all', 'Not specified'),
    ('under_100m', '<$100M'),
    ('100m_1b', '$100M–$1B'),
    ('1b_10b', '$1B–$10B'),
    ('over_10b', '>$10B'),
]
