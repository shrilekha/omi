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

# Coarser than OMI's own country dropdown on purpose — see the comment on
# GEOS in omi-benchmarks/backend/constants.py. Stored directly (no
# translation layer here, unlike OMI's backend/app.py), since this field
# has no question-content role, only a benchmark-lookup one.
GEOS = [
    ('all', 'Not specified'),
    ('India', 'India'),
    ('Middle East', 'Middle East'),
    ('International', 'International (other)'),
]

# INR-denominated — see the comment on REVENUE_BANDS in
# omi-benchmarks/backend/constants.py. Codes unchanged from the original USD
# bands, only the label.
REVENUE_BANDS = [
    ('all', 'Not specified'),
    ('under_100m', '<₹800 Cr'),
    ('100m_1b', '₹800 Cr – ₹8,000 Cr'),
    ('1b_10b', '₹8,000 Cr – ₹80,000 Cr'),
    ('over_10b', '>₹80,000 Cr'),
]
