# omi-deepdive — Per-App E2E Observability Question Bank
#
# HOW TO EDIT
#   Each dimension has a weight (must sum to 100 across all dimensions), an optional
#   "na_allowed" flag (only Real-User Monitoring uses this today, for backend/batch
#   apps with no direct end-user surface), one free-text "tool_question" asking what
#   currently covers this dimension (vendor-neutral — never assumes VuNet), and a list
#   of scored questions (5 options each, scored 1-5, 1 = least mature).
#
# This question set is intentionally vendor-agnostic throughout: every dimension asks
# what tool (if any) covers it today rather than assuming VuNet is the target platform.
# That's a deliberate correction from an earlier draft that framed this as a VuNet
# onboarding-status check — it isn't; it's a neutral E2E observability capability audit.

OWNERSHIP_QUESTIONS = [
    {
        "id": "owner_contact",
        "text": "Who owns this app's observability today (name/team)?",
    },
    {
        "id": "biggest_blocker",
        "text": "What's the single biggest blocker to improving this app's end-to-end "
                "observability today?",
    },
]

DIMENSIONS = [
    {
        "id": "network",
        "name": "Network Layer",
        "weight": 15,
        "na_allowed": False,
        "tool_question": {
            "id": "network_tool",
            "text": "What tool or platform, if any, currently provides network-layer "
                    "monitoring for this app's path — name it specifically (VuNet, "
                    "another vendor, in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "net1",
                "text": "Are the load balancers, firewalls, and WAN/link segments in "
                        "this app's actual request path instrumented and monitored — "
                        "not just generically monitored as shared infrastructure?",
                "hint": "Shared infra monitoring often exists without being mapped to "
                        "a specific application's path.",
                "options": [
                    "These components aren't monitored, or monitoring exists but isn't "
                    "mapped to this app's path.",
                    "Basic up/down status is monitored; performance and path-specific "
                    "behavior are not.",
                    "Key components in this app's path are monitored, but attribution "
                    "to this app is manual.",
                    "This app's network path components are monitored and clearly "
                    "attributed to this app.",
                    "Full instrumentation of this app's network path, automatically "
                    "correlated with application-level symptoms.",
                ],
            },
            {
                "id": "net2",
                "text": "Is network path performance — latency, jitter, packet loss — "
                        "measured specifically between this app's own tiers, not just "
                        "at the network perimeter?",
                "hint": "Requires active probing or IP SLA/synthetic path testing, not "
                        "just interface counters.",
                "options": [
                    "No path-level performance measurement between this app's tiers.",
                    "Basic ping/availability checks only; no latency, jitter, or "
                    "packet-loss data.",
                    "Path performance is measured for some tiers but not the full path.",
                    "Path performance is measured across all tiers, viewable on demand.",
                    "Path performance is continuously measured and alerted on for this "
                    "app's full path.",
                ],
            },
            {
                "id": "net3",
                "text": "Are DNS resolution and certificate/TLS health for this app's "
                        "endpoints actively monitored?",
                "hint": "DNS failures and certificate expiry are common causes of "
                        "app-facing outages that don't show up in server or app "
                        "metrics.",
                "options": [
                    "Not monitored — discovered only when users report an outage.",
                    "Manual periodic checks only.",
                    "Automated checks exist for TLS expiry or DNS, but not both.",
                    "Both DNS resolution and certificate health are actively monitored "
                    "and alerted.",
                    "Fully monitored and integrated into this app's overall health "
                    "dashboard.",
                ],
            },
            {
                "id": "net4",
                "text": "If this app depends on specific third-party network links — "
                        "bank-to-NPCI, inter-bank, MPLS/leased lines — are those links "
                        "monitored and clearly attributable to this app?",
                "hint": "A shared link's overall health doesn't tell you which "
                        "application is affected when it degrades.",
                "options": [
                    "We rely on the partner or telco to notify us of a link issue.",
                    "The link is monitored, but we can't tell which of our apps are "
                    "impacted.",
                    "The link is monitored and roughly mapped to a set of dependent "
                    "apps.",
                    "The link is monitored with clear per-app attribution during a "
                    "degradation.",
                    "Full dependency mapping — a link degradation automatically shows "
                    "the business impact on this app.",
                ],
            },
            {
                "id": "net5",
                "text": "When a network-layer issue occurs, does it show up correlated "
                        "with this app's symptoms automatically, or does someone have "
                        "to manually suspect and confirm the network is the cause?",
                "hint": "This is about correlation speed, not raw monitoring coverage.",
                "options": [
                    "Network is the default 'guess' with no way to confirm or rule it "
                    "out quickly.",
                    "Confirming a network cause takes manual cross-checking across "
                    "separate tools.",
                    "Some correlation exists but requires an engineer to pull it "
                    "together.",
                    "Automated correlation flags network as the likely cause within "
                    "minutes.",
                    "Fully automated — a network-layer issue and its app-level impact "
                    "appear together immediately.",
                ],
            },
        ],
    },
    {
        "id": "infra",
        "name": "Infrastructure & Compute",
        "weight": 10,
        "na_allowed": False,
        "tool_question": {
            "id": "infra_tool",
            "text": "What tool or platform, if any, currently monitors the compute/"
                    "infrastructure layer this app runs on — name it specifically "
                    "(VuNet, another vendor, in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "infra1",
                "text": "Are all compute components this app runs on — VMs, containers, "
                        "database instances, including anything shared/multi-tenant — "
                        "inventoried and monitored?",
                "hint": "Include anything this app depends on, even if it's a shared "
                        "platform owned by another team.",
                "options": [
                    "No reliable inventory of what this app runs on.",
                    "A manually maintained list exists; monitoring coverage is "
                    "inconsistent.",
                    "Inventory is accurate; most but not all components are monitored.",
                    "Full inventory and monitoring coverage, including shared "
                    "components.",
                    "Automated discovery keeps inventory and monitoring coverage "
                    "current in real time.",
                ],
            },
            {
                "id": "infra2",
                "text": "Is database-layer performance — query latency, connection pool "
                        "exhaustion, replication lag — monitored specifically for this "
                        "app's workload?",
                "hint": "Generic DB server CPU/memory metrics don't count as "
                        "query-level or app-specific visibility.",
                "options": [
                    "No DB-layer monitoring specific to this app.",
                    "Generic DB server metrics only; no query-level or app-specific "
                    "visibility.",
                    "Query-level metrics exist but aren't tied back to this app's "
                    "transactions.",
                    "DB performance is monitored and attributed to this app's "
                    "workload.",
                    "DB performance is fully correlated with this app's transaction "
                    "outcomes.",
                ],
            },
            {
                "id": "infra3",
                "text": "Is capacity/scaling behavior for this app tracked proactively, "
                        "or only discovered reactively during an incident?",
                "hint": "Reactive means finding out from an incident or a breach; "
                        "proactive means forecasting ahead of it.",
                "options": [
                    "Purely reactive — we add capacity after something breaks.",
                    "Manual periodic capacity reviews.",
                    "Trend-based forecasting for key components.",
                    "Automated forecasting with proactive alerts before exhaustion.",
                    "Predictive capacity intelligence tied to this app's actual "
                    "business growth.",
                ],
            },
            {
                "id": "infra4",
                "text": "If this app runs in containers/Kubernetes, is there pod-level "
                        "and namespace-level visibility, or does visibility stop at "
                        "the node? (If this app doesn't run in containers, answer for "
                        "the equivalent runtime unit.)",
                "hint": "Node-level metrics alone can hide a single misbehaving pod or "
                        "process.",
                "options": [
                    "No runtime-unit-level monitoring — treated like bare metal.",
                    "Node/host-level metrics only.",
                    "Pod/process-level metrics exist but aren't consistently used.",
                    "Full pod/process and namespace-level visibility in production.",
                    "Full container/runtime observability including resource limits, "
                    "restarts, and event tracking, tied to app health.",
                ],
            },
        ],
    },
    {
        "id": "apm",
        "name": "Application Performance (APM)",
        "weight": 15,
        "na_allowed": False,
        "tool_question": {
            "id": "apm_tool",
            "text": "What tool or platform, if any, currently provides APM/distributed "
                    "tracing for this app — name it specifically (VuNet, another "
                    "vendor, in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "apm1",
                "text": "Does this app have APM with code-level diagnostics, or only "
                        "infrastructure-level health checks?",
                "hint": "Code-level diagnostics means you can see which function/query "
                        "is slow, not just that the server is under load.",
                "options": [
                    "No APM — we rely on logs and user reports.",
                    "Basic APM exists but coverage is partial.",
                    "APM covers this app with dashboards; code-level diagnostics are "
                    "limited.",
                    "Full APM with code-level diagnostics for this app.",
                    "Full APM integrated with business observability and SLO tracking "
                    "for this app.",
                ],
            },
            {
                "id": "apm2",
                "text": "Can a single slow or failed request be traced across every "
                        "service, database call, and external call this app makes?",
                "hint": "Distributed tracing — following one request end-to-end "
                        "through a multi-service architecture.",
                "options": [
                    "No — each component is examined independently.",
                    "Logs are correlated manually using request IDs for some flows.",
                    "Distributed tracing exists for major services; gaps remain for "
                    "databases and external calls.",
                    "Full distributed tracing across services, databases, and "
                    "external calls.",
                    "Full tracing linked to business transaction outcomes and user "
                    "session context.",
                ],
            },
            {
                "id": "apm3",
                "text": "Are this app's third-party/API dependencies — payment "
                        "gateways, credit bureaus, KYC services, etc. — monitored for "
                        "latency and failure, specifically attributed to this app?",
                "hint": "Do you know a dependency is degrading before it causes a "
                        "visible failure in this app?",
                "options": [
                    "We find out when the dependency fails and it's reported to us.",
                    "Endpoint availability is monitored; response quality and latency "
                    "trends are not.",
                    "Latency and error rates are tracked for key dependencies.",
                    "Full dependency mapping with automated alerting on degradation.",
                    "Dependencies are part of this app's end-to-end observability with "
                    "business-impact scoring.",
                ],
            },
            {
                "id": "apm4",
                "text": "Does this app have defined SLOs, and is error-budget burn "
                        "actually alerted on?",
                "hint": "SLOs are internal targets, typically more granular than "
                        "external customer/regulator SLAs.",
                "options": [
                    "No SLOs — only informal uptime expectations.",
                    "External SLAs exist; internal SLOs are not formally defined.",
                    "SLOs are defined and tracked, but manually.",
                    "SLOs are automated with error-budget alerting.",
                    "SLO burn triggers automated, accountable escalation tied to "
                    "business impact.",
                ],
            },
            {
                "id": "apm5",
                "text": "Are deployments/releases for this app correlated with "
                        "performance regressions — can you tell a slowdown started "
                        "right after a specific release?",
                "hint": "Think of your last release that caused a quiet, gradual "
                        "regression rather than an obvious break.",
                "options": [
                    "No — deployment history and performance data are not connected.",
                    "Deployment timestamps are recorded but not compared against "
                    "performance trends.",
                    "Correlation is possible with manual investigation.",
                    "Deployments are automatically overlaid on performance "
                    "dashboards.",
                    "Automated regression detection flags a release as the likely "
                    "cause within minutes.",
                ],
            },
        ],
    },
    {
        "id": "rum",
        "name": "Real User Monitoring / Digital Experience",
        "weight": 10,
        "na_allowed": True,
        "na_label": "Not applicable — this app has no direct end-user interface "
                     "(backend/batch only).",
        "tool_question": {
            "id": "rum_tool",
            "text": "What tool or platform, if any, currently provides real-user "
                    "monitoring for this app — name it specifically (VuNet, another "
                    "vendor, in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "rum1",
                "text": "Is there real session-level real-user monitoring (not just "
                        "crash reporting) on this app's mobile and/or web surface?",
                "hint": "Session-level means real page/screen load times and errors "
                        "from actual user sessions, not just aggregate uptime.",
                "options": [
                    "No RUM — only app-store reviews or support tickets surface "
                    "issues.",
                    "Basic crash reporting only; no session-level page/screen "
                    "performance data.",
                    "Session-level RUM exists on one surface (e.g. mobile) but not "
                    "others.",
                    "Session-level RUM covers all this app's customer-facing "
                    "surfaces.",
                    "Full RUM across all surfaces, integrated with backend traces and "
                    "business KPIs.",
                ],
            },
            {
                "id": "rum2",
                "text": "Are page-load/app-load performance and error rates segmented "
                        "by device, OS, network type, and geography?",
                "hint": "Aggregate numbers can hide a severe problem affecting one "
                        "device type or region.",
                "options": [
                    "No segmentation — only aggregate numbers, if any.",
                    "Aggregate performance tracked; no meaningful segmentation.",
                    "Segmented by one dimension (e.g. OS) but not others.",
                    "Segmented across device, OS, network, and geography.",
                    "Fully segmented and used to prioritize fixes by real customer "
                    "impact.",
                ],
            },
            {
                "id": "rum3",
                "text": "Is RUM data correlated back to backend traces, so a slow "
                        "screen can be traced to its actual backend cause?",
                "hint": "Without this link, frontend and backend teams debug the same "
                        "incident with two disconnected data sets.",
                "options": [
                    "No connection between frontend and backend data at all.",
                    "Correlation requires manual cross-referencing of timestamps/"
                    "logs.",
                    "Correlation is possible for some flows with effort.",
                    "RUM and backend traces are linked for most critical journeys.",
                    "Fully automated frontend-to-backend correlation for every "
                    "journey.",
                ],
            },
            {
                "id": "rum4",
                "text": "For mobile specifically: are crash analytics, ANRs, and "
                        "app-store rating dips tied back to specific releases or "
                        "backend incidents?",
                "hint": "Answer for the mobile surface if this app has one; otherwise "
                        "answer for the closest equivalent client surface.",
                "options": [
                    "Not tracked, or tracked only via app-store reviews.",
                    "Crash analytics exist but aren't tied to releases or incidents.",
                    "Crashes are tied to releases; backend-incident correlation is "
                    "manual.",
                    "Crashes are automatically tied to both releases and backend "
                    "incidents.",
                    "Fully automated, with rating/crash trends feeding "
                    "release-quality decisions.",
                ],
            },
        ],
    },
    {
        "id": "synthetic",
        "name": "Synthetic / Proactive Monitoring",
        "weight": 10,
        "na_allowed": False,
        "tool_question": {
            "id": "synthetic_tool",
            "text": "What tool or platform, if any, currently runs synthetic/"
                    "proactive checks for this app — name it specifically (VuNet, "
                    "another vendor, in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "syn1",
                "text": "Are synthetic transactions run continuously for this app's "
                        "critical user journeys (e.g. login, key transaction, payment "
                        "step) — not just a URL ping?",
                "hint": "A URL responding with 200 OK doesn't mean the actual "
                        "journey behind it works.",
                "options": [
                    "No synthetic monitoring — issues are discovered by real users "
                    "first.",
                    "Periodic uptime/ping checks on a URL only.",
                    "Synthetic transactions run for at least one critical journey in "
                    "production.",
                    "Synthetic transactions cover all critical journeys for this "
                    "app.",
                    "Continuous synthetic testing across all journeys with "
                    "business-impact scoring per journey.",
                ],
            },
            {
                "id": "syn2",
                "text": "Do synthetic checks run from multiple relevant locations/"
                        "networks, not just from inside the monitoring vendor's own "
                        "network?",
                "hint": "A check from one data-center vantage point can miss issues "
                        "real customers hit on their own networks.",
                "options": [
                    "Single location/network only, if any.",
                    "A couple of locations, not representative of real customer "
                    "conditions.",
                    "Multiple locations covering major customer segments.",
                    "Broad location/network coverage matching real usage patterns.",
                    "Full coverage plus mobile-network/carrier-level synthetic "
                    "testing where relevant.",
                ],
            },
            {
                "id": "syn3",
                "text": "Does a synthetic failure trigger automated alerting/"
                        "escalation before real customers are affected at scale?",
                "hint": "Think about the gap between a synthetic check failing and a "
                        "human actually acting on it.",
                "options": [
                    "No automated escalation from synthetic failures.",
                    "Alerts exist but are noisy or frequently ignored.",
                    "Alerts are actioned but escalation is manual.",
                    "Automated escalation to the right team on synthetic failure.",
                    "Automated escalation plus auto-triage tied to business-impact "
                    "severity.",
                ],
            },
        ],
    },
    {
        "id": "biztxn",
        "name": "Business Transaction / Journey Observability",
        "weight": 25,
        "na_allowed": False,
        "tool_question": {
            "id": "biztxn_tool",
            "text": "What tool or platform, if any, currently provides business "
                    "transaction/journey tracing for this app — name it specifically "
                    "(VuNet, another vendor, in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "biz1",
                "text": "Does this app generate a durable unique business "
                        "transaction identifier (e.g. loan application ID, UPI/IMPS "
                        "reference, case ID) at the point of transaction initiation?",
                "hint": "This is about whether the identifier exists at all — "
                        "propagation and traceability are asked separately below.",
                "options": [
                    "No durable identifier is generated at initiation.",
                    "An identifier exists but isn't consistently generated for every "
                    "transaction.",
                    "A durable identifier is generated for most transaction types.",
                    "A durable identifier is generated for all transaction types on "
                    "this app.",
                    "A durable identifier is generated and standardized across all "
                    "transaction types and channels.",
                ],
            },
            {
                "id": "biz2",
                "text": "Is that identifier propagated and preserved across every "
                        "hop/service/queue this transaction passes through?",
                "hint": "An identifier that exists but gets dropped at one hop can't "
                        "support end-to-end tracing.",
                "options": [
                    "The identifier isn't propagated beyond the point of creation.",
                    "It's propagated through some hops but is lost at known "
                    "boundaries.",
                    "It's propagated through most hops with occasional gaps.",
                    "It's propagated end-to-end with rare, known exceptions.",
                    "It's propagated end-to-end with zero known gaps, including "
                    "through third parties where applicable.",
                ],
            },
            {
                "id": "biz3",
                "text": "Can that single identifier be used today to pull an "
                        "end-to-end trace of one specific customer's transaction, on "
                        "demand?",
                "hint": "This is the practical test: could you actually do this "
                        "right now if asked, and how long would it take?",
                "options": [
                    "No — reconstructing one transaction's path requires manual "
                    "log-hunting across teams.",
                    "Possible but takes hours and multiple teams.",
                    "Possible within an hour using existing tools.",
                    "A single lookup returns the full end-to-end trace within "
                    "minutes.",
                    "A single lookup returns the full end-to-end trace in near "
                    "real-time.",
                ],
            },
            {
                "id": "biz4",
                "text": "Are business KPIs for this app — success rate, completion "
                        "time, drop-off point — visible on a dashboard business "
                        "stakeholders actually use, not just IT?",
                "hint": "The test is actual regular use by business stakeholders, "
                        "not just theoretical access.",
                "options": [
                    "Business stakeholders get post-facto reports only.",
                    "Dashboards exist but are owned and used only by IT.",
                    "Business stakeholders have access but rarely use it during "
                    "incidents.",
                    "Business stakeholders have live dashboards they actively use.",
                    "IT and business share one live view with joint incident "
                    "response.",
                ],
            },
            {
                "id": "biz5",
                "text": "Is there a mapping from this app's technical failures to "
                        "business impact — e.g. 'X failed loan disbursals' rather "
                        "than just 'service returned 500 errors'?",
                "hint": "This is what lets an incident be prioritized and explained "
                        "in business terms, not just technical ones.",
                "options": [
                    "No mapping — technical errors and business impact are tracked "
                    "separately.",
                    "Mapping is done manually, after the fact, for major incidents "
                    "only.",
                    "Mapping exists for some failure types.",
                    "Most technical failures are automatically mapped to business "
                    "impact.",
                    "Full automated mapping feeding real-time business-impact "
                    "figures during an incident.",
                ],
            },
        ],
    },
    {
        "id": "correlation",
        "name": "Cross-Layer Correlation & Alerting",
        "weight": 10,
        "na_allowed": False,
        "tool_question": {
            "id": "correlation_tool",
            "text": "What tool or platform, if any, currently correlates data across "
                    "layers (network/infra/app/transaction) for this app — name it "
                    "specifically (VuNet, another vendor, in-house/open-source, or "
                    "none)?",
        },
        "questions": [
            {
                "id": "corr1",
                "text": "When this app has a P1, is there one correlated view "
                        "spanning network → infra → app → transaction, or do teams "
                        "pull data from separate tools and manually stitch it "
                        "together?",
                "hint": "Think about your last P1 war room and how many separate "
                        "screens/tools were open.",
                "options": [
                    "Fully manual — each team checks its own tool separately.",
                    "Some shared visibility exists but correlation is manual.",
                    "A partially correlated view exists for some layers.",
                    "A correlated view spans most layers for this app.",
                    "A single correlated view spans all layers automatically.",
                ],
            },
            {
                "id": "corr2",
                "text": "What's the actual measured MTTR for this app's last 2-3 "
                        "major incidents, and how much of that was spent locating "
                        "the root cause versus fixing it?",
                "hint": "Answer based on real incident data if you have it, not a "
                        "general impression.",
                "options": [
                    "Not measured, or the majority of MTTR is spent locating root "
                    "cause.",
                    "Roughly measured; root-cause location is still the majority of "
                    "MTTR.",
                    "Measured; root-cause location and fix time are roughly "
                    "balanced.",
                    "Measured; root-cause location is a small fraction of MTTR.",
                    "Root cause is identified almost immediately via automated "
                    "correlation; MTTR is dominated by fix time only.",
                ],
            },
            {
                "id": "corr3",
                "text": "Are alerts for this app deduplicated/correlated, or does "
                        "one root cause fire a flood of disconnected alerts across "
                        "teams?",
                "hint": "Alert fatigue from a single root cause is a strong signal "
                        "of missing cross-layer correlation.",
                "options": [
                    "One root cause routinely floods multiple teams with "
                    "disconnected alerts.",
                    "Some manual alert tuning exists but flooding still happens "
                    "regularly.",
                    "Deduplication exists for some alert sources.",
                    "Alerts are deduplicated and correlated to a single incident in "
                    "most cases.",
                    "Fully automated alert correlation into a single actionable "
                    "incident every time.",
                ],
            },
        ],
    },
    {
        "id": "logs",
        "name": "Log Observability",
        "weight": 5,
        "na_allowed": False,
        "tool_question": {
            "id": "logs_tool",
            "text": "What tool or platform, if any, currently centralizes logs for "
                    "this app — name it specifically (VuNet, another vendor, "
                    "in-house/open-source, or none)?",
        },
        "questions": [
            {
                "id": "log1",
                "text": "Are this app's logs — application, infra, network-device, DB "
                        "audit — centralized, or does someone SSH into boxes during "
                        "an incident?",
                "hint": "Count all log sources this app actually produces, not just "
                        "application logs.",
                "options": [
                    "Logs sit on individual systems; SSH access is needed to "
                    "investigate.",
                    "Some critical logs are centralized; coverage is under half.",
                    "Most logs are centralized; some gaps remain (e.g. network or DB "
                    "audit logs).",
                    "Comprehensive centralization across all log sources for this "
                    "app.",
                    "Full centralization with structured parsing/tagging and "
                    "real-time streaming.",
                ],
            },
            {
                "id": "log2",
                "text": "Is log retention/query speed for this app sufficient to "
                        "investigate an incident from a week ago in minutes, not "
                        "hours?",
                "hint": "Consider both how long logs are kept and how fast they can "
                        "actually be searched.",
                "options": [
                    "Logs are often purged before a week; retention is too short to "
                    "investigate.",
                    "Logs are retained but querying old data takes hours.",
                    "Retention is sufficient; query speed is inconsistent.",
                    "Retention and query speed are both sufficient for week-old "
                    "investigations.",
                    "Retention, query speed, and tiered storage are all optimized, "
                    "meeting any regulatory retention needs too.",
                ],
            },
        ],
    },
]

MATURITY_BANDS = [
    (0, 24, "Reactive"),
    (25, 44, "Aware"),
    (45, 64, "Structured"),
    (65, 81, "Proactive"),
    (82, 100, "Adaptive"),
]

assert sum(d["weight"] for d in DIMENSIONS) == 100, "Dimension weights must sum to 100"
