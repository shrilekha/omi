// ─────────────────────────────────────────────────────────────────────────────
// OMI — Observability Maturity Index: Questions & Scoring
//
// HOW TO EDIT THIS FILE
//   • Change question text or answer options freely — no other file needs to change.
//   • Each answer option has a 'score' from 1 (least mature) to 5 (most mature).
//   • Domains 1 (txnVariants) and 5 (compVariants) have sector + country variants.
//   • Domains 2–4 (app, infra, log) are the same for all sectors.
//   • To add a new variant, add a matching key to txnVariants AND compVariants.
//
// ARCHETYPE KEY CONVENTION
//   {sector}             — India (default) or country-agnostic
//   {sector}_gcc         — UAE / Saudi Arabia
//   {sector}_intl        — Singapore, UK, US, Australia, Other international
//
// SECTOR ARCHETYPE BASE KEYS
//   bfsi_regulated — Banks, NBFC, Insurance, Capital Markets
//   payments       — Payment aggregators, UPI / instant payment infrastructure, Wallets
//   government     — Central / state government, PSU
//   technology     — IT services, SaaS, other enterprise (country-agnostic; no country variant)
// ─────────────────────────────────────────────────────────────────────────────

// ─── DOMAIN 1: Business & Transaction Observability — sector × country variants ─

var txnVariants = {

  // ── BFSI REGULATED ────────────────────────────────────────────────────────

  bfsi_regulated: [
    {
      id: 'txn1',
      text: 'How do you currently monitor business transactions such as payments, loan disbursals, or trade settlements?',
      hint: 'How does your ops team know when a transaction has failed or degraded?',
      options: [
        { text: 'We rely on end-of-day reconciliation or customer complaints.', score: 1 },
        { text: 'We check application logs manually; dashboards exist but are disconnected from business KPIs.', score: 2 },
        { text: 'Basic APM is in place; we detect degradation but root cause takes hours.', score: 3 },
        { text: 'End-to-end transaction tracing across channels with near-real-time alerting.', score: 4 },
        { text: 'Full business transaction observability — IT metrics linked to business SLAs, failures trigger automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a critical transaction such as a payment gateway failure degrades, how quickly can your team identify root cause?',
      hint: 'Think of your last major P1 incident involving a customer-facing transaction.',
      options: [
        { text: 'Several hours to days — we trace manually across siloed tools.', score: 1 },
        { text: '1–4 hours — some tooling exists but RCA is largely manual.', score: 2 },
        { text: '30–60 minutes — we have correlated dashboards across most tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from business impact to infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to business KPIs.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can business leaders (not just IT) see real-time health of key transactions — for example UPI success rates or loan processing time?',
      hint: 'Think of executive dashboards, business ops centres, or war-room tools.',
      options: [
        { text: 'No — business leaders receive post-facto reports only.', score: 1 },
        { text: 'Some metrics exist in BI dashboards but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist but are maintained by IT and rarely used by business.', score: 3 },
        { text: 'Business leaders have live dashboards with threshold alerts on transaction KPIs.', score: 4 },
        { text: 'A unified Business Observability platform — IT and business share a single source of truth.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your synthetic or proactive transaction monitoring?',
      hint: 'Synthetic monitoring simulates user journeys to catch issues before real users are impacted.',
      options: [
        { text: 'No synthetic monitoring in place.', score: 1 },
        { text: 'Periodic ping or uptime checks on endpoints only.', score: 2 },
        { text: 'Synthetic transactions run for critical journeys in production.', score: 3 },
        { text: 'Covers all critical journeys across channels; SLA breach triggers auto-escalation.', score: 4 },
        { text: 'Fully automated synthetic testing in production and pre-prod with business-impact scoring per journey.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to revenue, customer experience, or regulatory SLAs?',
      hint: 'For example, do you measure "cost of downtime" or "transactions lost per second" in business terms?',
      options: [
        { text: 'No — IT and business metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — IT managers interpret metrics for business stakeholders.', score: 2 },
        { text: 'A few KPIs such as uptime SLA are shared between IT and business.', score: 3 },
        { text: 'Most observability KPIs map to business outcomes and are reviewed in joint forums.', score: 4 },
        { text: 'Full alignment — observability drives business SLA reporting, regulatory submissions, and P&L impact assessments.', score: 5 }
      ]
    }
  ],

  bfsi_regulated_gcc: [
    {
      id: 'txn1',
      text: 'How do you monitor retail banking transactions, card payments, trade finance settlements, or inter-bank transfers in your core banking environment?',
      hint: 'How does your ops team know when a customer payment or SWIFT/RTGS settlement has failed or degraded?',
      options: [
        { text: 'We rely on end-of-day reconciliation or branch and customer complaints.', score: 1 },
        { text: 'We check application logs manually; dashboards exist but are disconnected from business KPIs.', score: 2 },
        { text: 'Basic APM is in place; we detect degradation but root cause takes hours.', score: 3 },
        { text: 'End-to-end transaction tracing across channels with near-real-time alerting.', score: 4 },
        { text: 'Full business transaction observability — IT metrics linked to business SLAs, failures trigger automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a core banking outage, card network degradation, or SWIFT processing delay occurs, how quickly can your team identify root cause?',
      hint: 'Think of your last major P1 incident involving a payment gateway, ATM network, or inter-bank transfer.',
      options: [
        { text: 'Several hours to days — we trace manually across siloed tools.', score: 1 },
        { text: '1–4 hours — some tooling exists but RCA is largely manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from business impact to infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to business KPIs.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can business leaders see real-time health of key transactions — for example card authorisation rates, SWIFT settlement status, or trade finance completion volumes?',
      hint: 'Think of executive dashboards for banking operations centres, treasury war rooms, or retail banking NOC.',
      options: [
        { text: 'No — business leaders receive post-facto reports only.', score: 1 },
        { text: 'Some metrics exist in BI dashboards but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist but are owned by IT, not used by business leadership.', score: 3 },
        { text: 'Business leaders have live dashboards with threshold alerts on transaction KPIs.', score: 4 },
        { text: 'A unified Business Observability platform — IT and business share a single source of truth.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your synthetic or proactive monitoring of critical banking journeys — such as card transactions, online banking, or trade finance flows?',
      hint: 'Synthetic monitoring simulates customer journeys continuously to catch issues before real customers are impacted.',
      options: [
        { text: 'No synthetic monitoring in place.', score: 1 },
        { text: 'Periodic ping or uptime checks on banking portals only.', score: 2 },
        { text: 'Synthetic transactions run for critical journeys such as card authorisation in production.', score: 3 },
        { text: 'Covers all critical customer journeys; SLA breach triggers auto-escalation.', score: 4 },
        { text: 'Fully automated synthetic testing across all channels with business-impact scoring per journey.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to CBUAE operational resilience requirements, SAMA cybersecurity framework SLAs, or internal banking service commitments?',
      hint: 'For example, do you measure "card authorisation rate vs. network minimum" or "SWIFT settlement window adherence" as business metrics?',
      options: [
        { text: 'No — IT and business metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — IT managers brief business leaders during incidents.', score: 2 },
        { text: 'A few KPIs such as uptime SLA are shared between IT and business.', score: 3 },
        { text: 'Most observability KPIs map to business outcomes and regulatory thresholds; reviewed jointly.', score: 4 },
        { text: 'Full alignment — observability drives regulatory submissions, SLA reporting, and business impact assessments.', score: 5 }
      ]
    }
  ],

  bfsi_regulated_intl: [
    {
      id: 'txn1',
      text: 'How do you monitor critical banking transactions such as retail payments, card processing, trade finance settlements, or real-time payment scheme instructions (Faster Payments, FedNow, PayNow, NPP)?',
      hint: 'How does your ops team know when a payment instruction, settlement, or core banking function has failed or degraded?',
      options: [
        { text: 'We rely on end-of-day reconciliation or customer complaints.', score: 1 },
        { text: 'We check application logs manually; dashboards exist but are disconnected from business KPIs.', score: 2 },
        { text: 'Basic APM is in place; we detect degradation but root cause takes hours.', score: 3 },
        { text: 'End-to-end transaction tracing across channels with near-real-time alerting.', score: 4 },
        { text: 'Full business transaction observability — IT metrics linked to business SLAs, failures trigger automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a core banking system failure, payment processor outage, or real-time payment scheme degradation occurs, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving card processing, SWIFT, or a local real-time payment scheme.',
      options: [
        { text: 'Several hours to days — we trace manually across siloed tools.', score: 1 },
        { text: '1–4 hours — some tooling exists but RCA is largely manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from business impact to infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to business KPIs.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can business leaders see real-time health of key transactions — for example card authorisation rates, real-time payment settlement status, or trade finance completion volumes?',
      hint: 'Think of executive dashboards, treasury operations views, or customer service health indicators.',
      options: [
        { text: 'No — business leaders receive post-facto reports only.', score: 1 },
        { text: 'Some metrics exist in BI dashboards but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist but are owned by IT, not used by business leadership.', score: 3 },
        { text: 'Business leaders have live dashboards with threshold alerts on transaction KPIs.', score: 4 },
        { text: 'A unified Business Observability platform — IT and business share a single source of truth.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your synthetic or proactive monitoring of critical banking customer journeys?',
      hint: 'Synthetic monitoring simulates customer journeys continuously to catch degradations before real users are impacted.',
      options: [
        { text: 'No synthetic monitoring in place.', score: 1 },
        { text: 'Periodic ping or uptime checks on banking portals only.', score: 2 },
        { text: 'Synthetic transactions run for critical customer journeys in production.', score: 3 },
        { text: 'Covers all critical journeys across channels; SLA breach triggers auto-escalation.', score: 4 },
        { text: 'Fully automated synthetic testing across all channels with business-impact scoring per journey.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to your financial regulator\'s operational resilience requirements — such as MAS TRM, FCA operational resilience rules, APRA CPS 230, or FFIEC guidance?',
      hint: 'For example, do you measure "payment system availability vs. regulatory threshold" or "IT incident detection-to-notification time" as operational metrics?',
      options: [
        { text: 'No — IT and business metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — IT managers brief business leaders during incidents.', score: 2 },
        { text: 'A few KPIs such as uptime SLA are tracked against regulatory thresholds.', score: 3 },
        { text: 'Most observability KPIs map to regulatory requirements and are reviewed in joint IT-business forums.', score: 4 },
        { text: 'Full alignment — observability directly feeds regulatory reporting, incident notifications, and board-level resilience scorecards.', score: 5 }
      ]
    }
  ],

  // ── PAYMENTS ──────────────────────────────────────────────────────────────

  payments: [
    {
      id: 'txn1',
      text: 'How do you monitor transaction success rates across payment instruments such as UPI, IMPS, NACH, and cards?',
      hint: 'How does your ops team know when a payment instrument degrades or a settlement cycle is at risk?',
      options: [
        { text: 'We rely on end-of-day settlement reports or partner notifications.', score: 1 },
        { text: 'We have dashboards per instrument but they are siloed and not correlated.', score: 2 },
        { text: 'We detect volume drops or error spikes but tracing root cause takes hours.', score: 3 },
        { text: 'Real-time success-rate monitoring across all instruments with near-instant alerting.', score: 4 },
        { text: 'Full payment orchestration observability — each instrument mapped to SLA targets, failures trigger automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a payment settlement delay or gateway failure occurs, how quickly can your team identify and isolate root cause?',
      hint: 'Think of your last major incident involving NPCI, a card network, or an acquirer failure.',
      options: [
        { text: 'Several hours to days — teams work across siloed dashboards and logs.', score: 1 },
        { text: '1–4 hours — some tooling exists but correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards across most payment flows.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from transaction failure to network or processor root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to settlement SLAs.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can your finance and business operations team see real-time settlement status, failure rates, and reconciliation gaps?',
      hint: 'Think of NOC-style settlement dashboards, finance war rooms, or merchant reporting portals.',
      options: [
        { text: 'No — finance teams receive next-day reconciliation reports only.', score: 1 },
        { text: 'Some metrics available but lag by hours; not used during incidents.', score: 2 },
        { text: 'Near-real-time dashboards exist but are owned by IT, not the business team.', score: 3 },
        { text: 'Finance and operations have live settlement dashboards with exception alerting.', score: 4 },
        { text: 'A unified payments observability platform — IT, finance, and compliance share one view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How do you monitor and manage third-party dependencies such as acquirers, issuers, card networks, and NPCI infrastructure?',
      hint: 'Do you know about a partner degradation before your customers or merchants notice it?',
      options: [
        { text: 'We find out when the partner notifies us or merchants complain.', score: 1 },
        { text: 'We monitor endpoint availability but not response quality or latency trends.', score: 2 },
        { text: 'We track latency and error rates for key partners; alerting exists for major degradations.', score: 3 },
        { text: 'Full dependency map with automated alerting and auto-routing to backup paths on degradation.', score: 4 },
        { text: 'All third-party dependencies are part of end-to-end transaction observability with business-impact scoring.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to settlement SLAs, chargeback rates, or regulatory uptime mandates from NPCI or RBI?',
      hint: 'For example, do you track "UPI success rate vs. NPCI minimum" or "failed settlement value per hour" as business metrics?',
      options: [
        { text: 'No — technical metrics and business/regulatory KPIs are tracked separately.', score: 1 },
        { text: 'Informal alignment — operations managers interpret metrics for the business.', score: 2 },
        { text: 'A few regulatory KPIs such as uptime are tracked alongside technical metrics.', score: 3 },
        { text: 'Most observability KPIs map to settlement SLAs and regulatory thresholds; reviewed jointly.', score: 4 },
        { text: 'Full alignment — observability directly feeds regulatory reporting, merchant SLAs, and chargeback analysis.', score: 5 }
      ]
    }
  ],

  payments_intl: [
    {
      id: 'txn1',
      text: 'How do you monitor transaction success rates across payment instruments such as cards, account-to-account transfers, SWIFT/SEPA, real-time payment rails (Faster Payments, FedNow, PayNow), and digital wallets?',
      hint: 'How does your ops team know when a payment rail or processor degrades before merchants or customers notice?',
      options: [
        { text: 'We rely on end-of-day settlement reports or partner notifications.', score: 1 },
        { text: 'We have dashboards per instrument but they are siloed and not correlated.', score: 2 },
        { text: 'We detect volume drops or error spikes but tracing root cause takes hours.', score: 3 },
        { text: 'Real-time success-rate monitoring across all payment instruments with near-instant alerting.', score: 4 },
        { text: 'Full payment orchestration observability — every instrument mapped to SLA targets, failures trigger automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a settlement failure, acquirer outage, or payment gateway degradation occurs, how quickly can your team isolate root cause?',
      hint: 'Think of your last major incident involving a card network, real-time payment scheme, or correspondent bank failure.',
      options: [
        { text: 'Several hours to days — teams work across siloed dashboards and logs.', score: 1 },
        { text: '1–4 hours — some tooling exists but correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most payment flows.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from transaction failure to network or processor root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to settlement SLAs.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can your finance and operations team see real-time settlement status, card authorisation rates, and reconciliation exceptions?',
      hint: 'Think of NOC-style settlement dashboards, finance operations centres, or merchant exception reporting portals.',
      options: [
        { text: 'No — finance teams receive next-day reconciliation reports only.', score: 1 },
        { text: 'Some metrics available but lag by hours; not used during incidents.', score: 2 },
        { text: 'Near-real-time dashboards exist but are owned by IT, not the finance or operations team.', score: 3 },
        { text: 'Finance and operations have live settlement dashboards with exception alerting.', score: 4 },
        { text: 'A unified payments observability platform — IT, finance, and compliance share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How do you monitor third-party dependencies — card networks, acquirers, real-time payment scheme operators, and correspondent banks?',
      hint: 'Do you detect partner degradations before they cascade to merchants or end customers?',
      options: [
        { text: 'We find out when the partner notifies us or merchants complain.', score: 1 },
        { text: 'We monitor endpoint availability but not response quality or latency trends.', score: 2 },
        { text: 'We track latency and error rates for key partners; alerting exists for major degradations.', score: 3 },
        { text: 'Full dependency map with automated alerting and auto-routing to backup paths on degradation.', score: 4 },
        { text: 'All third-party dependencies are part of end-to-end transaction observability with business-impact scoring.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to card network performance mandates, real-time payment scheme SLAs, or PCI-DSS uptime requirements?',
      hint: 'For example, do you track "card authorisation rate vs. Visa/MC minimum threshold" or "real-time payment latency vs. scheme SLA" as business metrics?',
      options: [
        { text: 'No — technical metrics and business/regulatory KPIs are tracked separately.', score: 1 },
        { text: 'Informal alignment — operations managers interpret metrics for the business.', score: 2 },
        { text: 'A few payment scheme or regulatory KPIs are tracked alongside technical metrics.', score: 3 },
        { text: 'Most observability KPIs map to scheme SLAs and regulatory thresholds; reviewed jointly.', score: 4 },
        { text: 'Full alignment — observability directly feeds scheme reporting, merchant SLA dashboards, and chargeback analysis.', score: 5 }
      ]
    }
  ],

  // ── GOVERNMENT ────────────────────────────────────────────────────────────

  government: [
    {
      id: 'txn1',
      text: 'How do you currently monitor citizen-facing service transactions across portals and platforms such as e-Seva, UMANG, DigiLocker, or CSC?',
      hint: 'How does your IT team know when a citizen service has degraded or a disbursement portal is failing?',
      options: [
        { text: 'We find out through citizen complaints or helpdesk escalations.', score: 1 },
        { text: 'We check server logs manually; some dashboards exist but do not reflect service outcomes.', score: 2 },
        { text: 'Uptime monitoring is in place for key portals; service-level failures take hours to diagnose.', score: 3 },
        { text: 'End-to-end transaction tracing across citizen journeys with near-real-time alerting.', score: 4 },
        { text: 'Full citizen service observability — IT metrics linked to programme SLAs and citizen experience outcomes.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a critical government service portal degrades — such as a pension disbursement or certificate issuance system — how quickly can your team identify root cause?',
      hint: 'Think of your last major service-disruption incident on a citizen-facing platform.',
      options: [
        { text: 'Several hours to days — teams coordinate manually across siloed departments.', score: 1 },
        { text: '1–4 hours — some tooling exists but RCA depends on manual log searches.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from citizen-facing impact to infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection with automated escalation to the programme team.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can programme officers or department heads see real-time health of key citizen services — for example, portal availability or daily transaction completion rates?',
      hint: 'Think of operations dashboards used by programme management, not just IT.',
      options: [
        { text: 'No — programme teams receive weekly or monthly usage reports only.', score: 1 },
        { text: 'Some metrics available in BI tools but they lag by hours or days.', score: 2 },
        { text: 'Near-real-time dashboards exist for IT teams; business stakeholders are not regular users.', score: 3 },
        { text: 'Programme officers have live dashboards with threshold alerts on citizen service KPIs.', score: 4 },
        { text: 'A unified digital service observability platform — IT and programme management share one view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive monitoring of citizen portal availability and end-to-end transaction completion?',
      hint: 'Synthetic monitoring tests citizen journeys continuously to catch issues before real users are impacted.',
      options: [
        { text: 'No proactive monitoring — we only know of failures when citizens report them.', score: 1 },
        { text: 'Periodic ping or uptime checks on portal URLs.', score: 2 },
        { text: 'Synthetic transactions run for critical citizen journeys in production.', score: 3 },
        { text: 'Covers all critical citizen journeys; SLA breach triggers auto-escalation to the responsible team.', score: 4 },
        { text: 'Fully automated synthetic testing with business-impact scoring per citizen service.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to citizen service SLAs, programme delivery targets, or government digital mission metrics?',
      hint: 'For example, do you measure "portal downtime cost in citizen transactions" or "failed disbursements per day" as a programme metric?',
      options: [
        { text: 'No — IT metrics and programme delivery metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — IT managers brief programme officers during incidents.', score: 2 },
        { text: 'A few shared KPIs such as uptime SLAs are tracked between IT and programme teams.', score: 3 },
        { text: 'Most observability KPIs map to programme delivery outcomes and are reviewed in joint forums.', score: 4 },
        { text: 'Full alignment — observability feeds programme KPI dashboards, ministerial reporting, and audit submissions.', score: 5 }
      ]
    }
  ],

  government_intl: [
    {
      id: 'txn1',
      text: 'How do you monitor citizen-facing digital service transactions across government portals, apps, and integrated service platforms?',
      hint: 'How does your team know when a permit application, benefit disbursement, or licensing transaction has failed or degraded?',
      options: [
        { text: 'We find out through citizen complaints or helpdesk escalations.', score: 1 },
        { text: 'We check server logs manually; some dashboards exist but do not reflect service outcomes.', score: 2 },
        { text: 'Uptime monitoring is in place for key portals; service-level failures take hours to diagnose.', score: 3 },
        { text: 'End-to-end transaction tracing across citizen journeys with near-real-time alerting.', score: 4 },
        { text: 'Full citizen service observability — IT metrics linked to programme SLAs and citizen experience outcomes.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a critical government digital service degrades — such as a benefits platform, licensing system, or emergency service portal — how quickly can your team identify root cause?',
      hint: 'Think of your last major incident on a citizen-facing portal or integrated government service.',
      options: [
        { text: 'Several hours to days — teams coordinate manually across siloed departments.', score: 1 },
        { text: '1–4 hours — some tooling exists but RCA depends on manual log searches.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from citizen-facing impact to infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection with automated escalation to the programme team.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can programme managers or department heads see real-time health of key digital services — for example portal availability, transaction completion rates, or application processing volumes?',
      hint: 'Think of performance dashboards for programme owners and digital service managers, not just the IT operations team.',
      options: [
        { text: 'No — programme teams receive weekly or monthly usage reports only.', score: 1 },
        { text: 'Some metrics available in BI tools but they lag by hours or days.', score: 2 },
        { text: 'Near-real-time dashboards exist for IT; business stakeholders are not regular users.', score: 3 },
        { text: 'Programme managers have live dashboards with threshold alerts on digital service KPIs.', score: 4 },
        { text: 'A unified digital service observability platform — IT and programme management share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive monitoring of citizen-facing service availability and end-to-end transaction completion?',
      hint: 'Synthetic monitoring tests citizen journeys continuously to catch degradations before real users are affected.',
      options: [
        { text: 'No proactive monitoring — we only know of failures when citizens report them.', score: 1 },
        { text: 'Periodic ping or uptime checks on portal URLs.', score: 2 },
        { text: 'Synthetic transactions run for critical citizen journeys in production.', score: 3 },
        { text: 'Covers all critical citizen journeys; SLA breach triggers auto-escalation to the responsible team.', score: 4 },
        { text: 'Fully automated synthetic testing with business-impact scoring per citizen service.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to digital service delivery targets, public service charter commitments, or government programme outcomes?',
      hint: 'For example, do you measure "citizen journey completion rate vs. target" or "portal availability vs. published SLA" as programme performance metrics?',
      options: [
        { text: 'No — IT metrics and programme delivery metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — IT managers brief programme officers during incidents.', score: 2 },
        { text: 'A few shared KPIs such as uptime are tracked between IT and programme teams.', score: 3 },
        { text: 'Most observability KPIs map to programme delivery outcomes and are reviewed in joint forums.', score: 4 },
        { text: 'Full alignment — observability feeds programme dashboards, ministerial reporting, and audit submissions.', score: 5 }
      ]
    }
  ],

  // ── TECHNOLOGY (country-agnostic) ─────────────────────────────────────────

  technology: [
    {
      id: 'txn1',
      text: 'How do you monitor critical customer-facing API transactions and SaaS service delivery?',
      hint: 'How does your team know when an API integration or customer-facing feature has degraded?',
      options: [
        { text: 'We find out through customer support tickets or NPS drops.', score: 1 },
        { text: 'We monitor service uptime; API-level health depends on customer reports.', score: 2 },
        { text: 'API error rates and latencies are tracked; diagnosing root cause takes time.', score: 3 },
        { text: 'End-to-end API transaction tracing with near-real-time alerting on customer-impacting degradations.', score: 4 },
        { text: 'Full product observability — every customer journey mapped to SLA targets with automated triage on failure.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a production deployment or API failure degrades customer experience, how quickly can your team identify root cause?',
      hint: 'Think of your last major production incident affecting customers or API consumers.',
      options: [
        { text: 'Several hours to days — debugging requires manual log analysis across services.', score: 1 },
        { text: '1–4 hours — some tooling exists but correlation is largely manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards across most services and dependencies.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from customer impact to service root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection with deployment context and customer impact scoring.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can your customer success or product team see real-time service health and SLA adherence per customer account or tenant?',
      hint: 'Think of CS dashboards, account health scores, or per-tenant SLA tracking.',
      options: [
        { text: 'No — customer-facing SLA data is only available after manual compilation.', score: 1 },
        { text: 'Some aggregate health metrics available but not per customer or per tenant.', score: 2 },
        { text: 'Near-real-time dashboards exist for the engineering team; CS does not have direct access.', score: 3 },
        { text: 'Customer success has live dashboards with per-account health and SLA alerts.', score: 4 },
        { text: 'A unified product observability platform shared by engineering, CS, and account management.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your synthetic or continuous testing of customer-critical API endpoints and user journeys?',
      hint: 'Synthetic monitoring detects issues before real customers are affected.',
      options: [
        { text: 'No synthetic monitoring — issues are discovered by customers first.', score: 1 },
        { text: 'Periodic health checks on key API endpoints.', score: 2 },
        { text: 'Synthetic tests run for critical customer journeys in production.', score: 3 },
        { text: 'Covers all critical API and user journeys; SLA breach triggers automated alerting.', score: 4 },
        { text: 'Continuous synthetic testing in production and staging with business-impact scoring per journey.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to customer SLAs, ARR at risk, or contractual uptime commitments?',
      hint: 'For example, do you track "SLA breach exposure in ARR" or "P95 API latency vs. contractual SLA" as business metrics?',
      options: [
        { text: 'No — engineering metrics and customer SLA commitments are tracked separately.', score: 1 },
        { text: 'Informal alignment — engineering leads brief account managers during incidents.', score: 2 },
        { text: 'Uptime SLAs are tracked and shared with customers; internal SLOs are not formalised.', score: 3 },
        { text: 'Most observability KPIs map to customer commitments and are reviewed in joint engineering-CS forums.', score: 4 },
        { text: 'Full alignment — observability feeds customer SLA reporting, renewal risk dashboards, and executive scorecards.', score: 5 }
      ]
    }
  ],

  // ── RETAIL & E-COMMERCE ───────────────────────────────────────────────────

  retail: [
    {
      id: 'txn1',
      text: 'How do you monitor order-to-cash transaction health across your e-commerce, POS, and omnichannel platforms?',
      hint: 'How does your ops team know when checkout is failing, payments are declining, or orders are stuck in processing at scale?',
      options: [
        { text: 'We find out through customer complaints or a spike in support tickets.', score: 1 },
        { text: 'We have dashboards for each channel but they are siloed and not correlated.', score: 2 },
        { text: 'We detect error spikes in checkout or payment but root cause takes time.', score: 3 },
        { text: 'Real-time order and payment health monitoring across all channels with near-instant alerting.', score: 4 },
        { text: 'Full omnichannel transaction observability — every customer journey mapped to conversion and revenue KPIs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a flash sale, seasonal peak, or payment gateway failure causes transaction degradation, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving checkout, payment processing, or order management during a high-traffic period.',
      options: [
        { text: 'Several hours — we debug manually across siloed tools after the event.', score: 1 },
        { text: '1–4 hours — some tooling exists but correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most e-commerce tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from customer-facing impact to payment or infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to GMV and conversion metrics.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can your merchandising, commercial, or operations teams see real-time transaction health — such as cart abandonment rate, checkout success rate, or order processing backlog?',
      hint: 'Think of business war rooms during sale events, e-commerce NOC dashboards, or store operations centres.',
      options: [
        { text: 'No — business teams get post-event reports only.', score: 1 },
        { text: 'Some metrics available in BI tools but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist for IT; business teams are not regular users.', score: 3 },
        { text: 'Business teams have live dashboards with threshold alerts on transaction and conversion KPIs.', score: 4 },
        { text: 'A unified commerce observability platform — IT, merchandising, and commercial share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive monitoring of critical customer journeys — such as product search, add-to-cart, checkout, and payment confirmation?',
      hint: 'Synthetic monitoring simulates complete purchase journeys to catch degradations before customers abandon their carts.',
      options: [
        { text: 'No synthetic monitoring — issues are discovered by customers first.', score: 1 },
        { text: 'Periodic uptime checks on the homepage and checkout URL.', score: 2 },
        { text: 'Synthetic purchase journeys run for critical flows in production.', score: 3 },
        { text: 'Covers all critical customer journeys across channels; conversion impact triggers auto-escalation.', score: 4 },
        { text: 'Continuous synthetic testing with GMV-impact scoring per journey degradation.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to GMV at risk, conversion rate SLAs, or revenue-per-minute impact during peak events?',
      hint: 'For example, do you track "checkout success rate vs. target" or "estimated GMV lost per minute of downtime" as business metrics?',
      options: [
        { text: 'No — IT metrics and business revenue metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — engineering leads brief commercial teams during incidents.', score: 2 },
        { text: 'Uptime SLAs are tracked; conversion and GMV impact is calculated retrospectively.', score: 3 },
        { text: 'Most observability KPIs map to commercial outcomes and are reviewed in joint IT-business forums.', score: 4 },
        { text: 'Full alignment — observability directly drives incident prioritisation, sale-event capacity planning, and P&L impact reporting.', score: 5 }
      ]
    }
  ],

  retail_intl: [
    {
      id: 'txn1',
      text: 'How do you monitor order-to-cash transaction health across your e-commerce, POS, and omnichannel platforms?',
      hint: 'How does your ops team know when checkout is failing, payments are declining, or orders are stuck in processing at scale?',
      options: [
        { text: 'We find out through customer complaints or a spike in support tickets.', score: 1 },
        { text: 'We have dashboards for each channel but they are siloed and not correlated.', score: 2 },
        { text: 'We detect error spikes in checkout or payment but root cause takes time.', score: 3 },
        { text: 'Real-time order and payment health monitoring across all channels with near-instant alerting.', score: 4 },
        { text: 'Full omnichannel transaction observability — every customer journey mapped to conversion and revenue KPIs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a flash sale, seasonal peak, or payment gateway failure causes transaction degradation, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving checkout, payment processing, or order management during a high-traffic period.',
      options: [
        { text: 'Several hours — we debug manually across siloed tools after the event.', score: 1 },
        { text: '1–4 hours — some tooling exists but correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most e-commerce tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from customer-facing impact to payment or infrastructure root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to GMV and conversion metrics.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can your merchandising, commercial, or operations teams see real-time transaction health — such as cart abandonment rate, checkout success rate, or order processing backlog?',
      hint: 'Think of business war rooms during sale events, e-commerce NOC dashboards, or store operations centres.',
      options: [
        { text: 'No — business teams get post-event reports only.', score: 1 },
        { text: 'Some metrics available in BI tools but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist for IT; business teams are not regular users.', score: 3 },
        { text: 'Business teams have live dashboards with threshold alerts on transaction and conversion KPIs.', score: 4 },
        { text: 'A unified commerce observability platform — IT, merchandising, and commercial share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive monitoring of critical customer journeys — such as product search, add-to-cart, checkout, and payment confirmation?',
      hint: 'Synthetic monitoring simulates complete purchase journeys to catch degradations before customers abandon their carts.',
      options: [
        { text: 'No synthetic monitoring — issues are discovered by customers first.', score: 1 },
        { text: 'Periodic uptime checks on the homepage and checkout URL.', score: 2 },
        { text: 'Synthetic purchase journeys run for critical flows in production.', score: 3 },
        { text: 'Covers all critical customer journeys across channels; conversion impact triggers auto-escalation.', score: 4 },
        { text: 'Continuous synthetic testing with GMV-impact scoring per journey degradation.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to GMV at risk, conversion rate SLAs, or revenue-per-minute impact during peak events?',
      hint: 'For example, do you track "checkout success rate vs. target" or "estimated revenue lost per minute of downtime" as business metrics?',
      options: [
        { text: 'No — IT metrics and business revenue metrics are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — engineering leads brief commercial teams during incidents.', score: 2 },
        { text: 'Uptime SLAs are tracked; conversion and revenue impact is calculated retrospectively.', score: 3 },
        { text: 'Most observability KPIs map to commercial outcomes and are reviewed in joint IT-business forums.', score: 4 },
        { text: 'Full alignment — observability directly drives incident prioritisation, peak-event capacity planning, and revenue impact reporting.', score: 5 }
      ]
    }
  ],

  // ── TELECOM ───────────────────────────────────────────────────────────────

  telecom: [
    {
      id: 'txn1',
      text: 'How do you monitor the health of critical telecom service transactions — such as call session establishment, data bearer activation, SMS delivery, VoIP quality, and roaming transactions?',
      hint: 'How does your NOC know when call completion rates are dropping, data sessions are failing, or a roaming partner degradation is impacting subscribers?',
      options: [
        { text: 'We rely on subscriber complaints or billing anomalies to detect service degradations.', score: 1 },
        { text: 'We monitor network element alarms but service-level transaction health is not tracked.', score: 2 },
        { text: 'Key service KPIs such as call drop rate and data throughput are tracked but cross-domain RCA takes hours.', score: 3 },
        { text: 'Real-time service transaction monitoring across voice, data, and messaging with near-instant alerting.', score: 4 },
        { text: 'Full end-to-end service observability — network, IT, and BSS metrics linked to subscriber experience KPIs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a network element failure, core network congestion, or interconnect routing issue degrades service, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving an MSC, PGW/UPF, IMS core, or interconnect partner failure.',
      options: [
        { text: 'Several hours to days — NOC teams coordinate manually across siloed network and IT systems.', score: 1 },
        { text: '1–4 hours — some tooling exists but cross-domain correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most network and IT tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from service degradation to network or IT root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to subscriber experience and ARPU impact.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can commercial, regulatory, and customer care teams see real-time service health — such as call completion rates, data throughput by circle, or VoIP MOS scores — without relying on IT or NOC to pull reports?',
      hint: 'Think of network health dashboards accessible to commercial, customer care, and regulatory compliance teams.',
      options: [
        { text: 'No — only NOC engineers have access to real-time service data.', score: 1 },
        { text: 'Some service metrics shared with CXO team during incidents; not a regular operational view.', score: 2 },
        { text: 'Near-real-time dashboards exist for NOC; commercial and regulatory teams do not have direct access.', score: 3 },
        { text: 'Commercial and regulatory teams have live dashboards with threshold alerts on service KPIs.', score: 4 },
        { text: 'A unified telecom service observability platform shared across NOC, commercial, CX, and regulatory functions.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive service monitoring — synthetic call tests, data bearer tests, and end-to-end service quality checks across your network?',
      hint: 'Synthetic testing periodically initiates real calls and data sessions to detect service degradations before subscribers notice.',
      options: [
        { text: 'No synthetic testing — service degradations are discovered through subscriber complaints.', score: 1 },
        { text: 'Periodic endpoint availability checks; no live call or data session testing.', score: 2 },
        { text: 'Synthetic call and data tests run in key locations; coverage is partial.', score: 3 },
        { text: 'Comprehensive synthetic testing across all circles and service types; SLA breach triggers auto-escalation.', score: 4 },
        { text: 'Continuous synthetic service testing with subscriber experience scoring and automated incident creation.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to TRAI Quality of Service benchmarks, interconnect SLAs, or subscriber experience commitments?',
      hint: 'For example, do you measure "call drop rate vs. TRAI benchmark" or "data throughput vs. advertised speed" as regulatory and commercial KPIs?',
      options: [
        { text: 'No — network performance metrics and TRAI/business KPIs are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — NOC engineers prepare TRAI KPI reports manually each quarter.', score: 2 },
        { text: 'TRAI QoS benchmarks are tracked in a compliance dashboard; operational observability is separate.', score: 3 },
        { text: 'Most observability KPIs map to TRAI benchmarks and subscriber SLAs; reviewed jointly by NOC and commercial.', score: 4 },
        { text: 'Full alignment — observability feeds TRAI regulatory submissions, interconnect SLA reporting, and subscriber experience dashboards.', score: 5 }
      ]
    }
  ],

  telecom_intl: [
    {
      id: 'txn1',
      text: 'How do you monitor the health of critical telecom service transactions — such as call session establishment, data bearer activation, SMS delivery, VoIP quality, and roaming transactions?',
      hint: 'How does your NOC know when call completion rates are dropping, data sessions are failing, or a roaming partner degradation is impacting subscribers?',
      options: [
        { text: 'We rely on subscriber complaints or billing anomalies to detect service degradations.', score: 1 },
        { text: 'We monitor network element alarms but service-level transaction health is not tracked.', score: 2 },
        { text: 'Key service KPIs such as call drop rate and data throughput are tracked but cross-domain RCA takes hours.', score: 3 },
        { text: 'Real-time service transaction monitoring across voice, data, and messaging with near-instant alerting.', score: 4 },
        { text: 'Full end-to-end service observability — network, IT, and BSS metrics linked to subscriber experience KPIs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When a network element failure, core network congestion, or interconnect routing issue degrades service, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving a core network node, IMS platform, or international roaming partner failure.',
      options: [
        { text: 'Several hours to days — NOC teams coordinate manually across siloed network and IT systems.', score: 1 },
        { text: '1–4 hours — some tooling exists but cross-domain correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most network and IT tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from service degradation to network or IT root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to subscriber experience and ARPU impact.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can commercial, regulatory, and customer care teams see real-time service health — such as call completion rates, data throughput by region, or VoIP MOS scores — without relying on the NOC to pull reports?',
      hint: 'Think of network health dashboards accessible to commercial, customer care, and regulatory teams.',
      options: [
        { text: 'No — only NOC engineers have access to real-time service data.', score: 1 },
        { text: 'Some service metrics shared with leadership during major incidents; not a regular operational view.', score: 2 },
        { text: 'Near-real-time dashboards exist for NOC; commercial and regulatory teams do not have direct access.', score: 3 },
        { text: 'Commercial and regulatory teams have live dashboards with threshold alerts on service KPIs.', score: 4 },
        { text: 'A unified telecom service observability platform shared across NOC, commercial, CX, and regulatory functions.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive service monitoring — synthetic call tests, data bearer tests, and end-to-end service quality checks across your network footprint?',
      hint: 'Synthetic testing periodically initiates real calls and data sessions to detect service degradations before subscribers notice.',
      options: [
        { text: 'No synthetic testing — service degradations are discovered through subscriber complaints.', score: 1 },
        { text: 'Periodic endpoint availability checks; no live call or data session testing.', score: 2 },
        { text: 'Synthetic call and data tests run in key locations; coverage is partial.', score: 3 },
        { text: 'Comprehensive synthetic testing across all regions and service types; SLA breach triggers auto-escalation.', score: 4 },
        { text: 'Continuous synthetic service testing with subscriber experience scoring and automated incident creation.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to your national regulator\'s Quality of Service benchmarks, interconnect SLAs, or subscriber experience commitments?',
      hint: 'For example, do you measure "call drop rate vs. Ofcom/FCC benchmark" or "data throughput vs. advertised speed" as regulatory and commercial KPIs?',
      options: [
        { text: 'No — network performance metrics and regulatory/business KPIs are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — NOC engineers prepare regulatory KPI reports manually each quarter.', score: 2 },
        { text: 'Regulatory QoS benchmarks are tracked in a compliance dashboard; operational observability is separate.', score: 3 },
        { text: 'Most observability KPIs map to regulatory benchmarks and subscriber SLAs; reviewed jointly by NOC and commercial.', score: 4 },
        { text: 'Full alignment — observability feeds regulatory submissions, interconnect SLA reporting, and subscriber experience dashboards.', score: 5 }
      ]
    }
  ],

  // ── ENERGY & UTILITIES ────────────────────────────────────────────────────

  energy: [
    {
      id: 'txn1',
      text: 'How do you monitor critical operational transactions — such as grid dispatch events, smart meter reads, billing cycle processing, and outage management system updates?',
      hint: 'How does your operations team know when a billing run has stalled, a SCADA event has not been processed, or smart meter data collection is falling behind schedule?',
      options: [
        { text: 'We find out through manual checks, field team reports, or consumer complaints.', score: 1 },
        { text: 'We monitor system availability; transaction-level health is not tracked in real time.', score: 2 },
        { text: 'Key operational KPIs are tracked but cross-system RCA takes hours.', score: 3 },
        { text: 'Real-time monitoring of grid events, metering, and billing with near-instant alerting on failures.', score: 4 },
        { text: 'Full operational transaction observability — SCADA, OMS, billing, and metering linked to regulatory SLAs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When an outage management system failure, SCADA integration error, or billing processing degradation occurs, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving an ERP billing failure, OMS delay, or smart metering data gap.',
      options: [
        { text: 'Several hours to days — OT and IT teams coordinate manually across siloed systems.', score: 1 },
        { text: '1–4 hours — some tooling exists but cross-system correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most OT and IT tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from operational event to system root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to grid SLAs and regulatory reliability indices.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can operations leadership and commercial teams see real-time health of key business processes — such as outage resolution SLAs, billing completion rates, or metering data freshness?',
      hint: 'Think of grid operations NOC dashboards, commercial billing health views, or field operations management centres.',
      options: [
        { text: 'No — leadership receives periodic operational reports only.', score: 1 },
        { text: 'Some metrics available in BI tools but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist for operations teams; leadership does not have direct access.', score: 3 },
        { text: 'Operations leadership has live dashboards with alerts on grid, billing, and metering KPIs.', score: 4 },
        { text: 'A unified utility operations platform — grid, commercial, and regulatory teams share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive health monitoring of critical operational systems — SCADA, OMS, billing, and smart metering infrastructure?',
      hint: 'Proactive health checks detect processing failures before they cascade to consumer billing errors or regulatory reporting gaps.',
      options: [
        { text: 'No proactive monitoring — failures are discovered through field reports or billing exceptions.', score: 1 },
        { text: 'Periodic availability checks on key servers; no transaction-level health monitoring.', score: 2 },
        { text: 'Key system health metrics monitored; end-to-end transaction health is not proactively tested.', score: 3 },
        { text: 'Proactive health checks across SCADA, OMS, and billing with auto-escalation on failure.', score: 4 },
        { text: 'Continuous end-to-end operational monitoring with regulatory reliability impact scoring.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to CERC / SERC reliability indices such as SAIDI and SAIFI, billing accuracy SLAs, or smart metering data quality targets?',
      hint: 'For example, do you track "meter read success rate vs. regulatory target" or "outage duration contribution to SAIDI" as operational KPIs?',
      options: [
        { text: 'No — IT metrics and regulatory performance indices are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — operations managers compile regulatory KPI reports manually.', score: 2 },
        { text: 'CERC/SERC KPIs are tracked in a compliance tool; operational observability is separate.', score: 3 },
        { text: 'Most observability KPIs map to regulatory targets and are reviewed jointly by operations and compliance.', score: 4 },
        { text: 'Full alignment — observability directly feeds regulatory submissions, SAIDI/SAIFI reporting, and tariff proceedings.', score: 5 }
      ]
    }
  ],

  energy_intl: [
    {
      id: 'txn1',
      text: 'How do you monitor critical operational transactions — such as grid dispatch events, smart meter reads, billing cycle processing, and outage management system updates?',
      hint: 'How does your operations team know when a billing run has stalled, a SCADA event has not been processed, or smart meter data collection is falling behind schedule?',
      options: [
        { text: 'We find out through manual checks, field team reports, or consumer complaints.', score: 1 },
        { text: 'We monitor system availability; transaction-level health is not tracked in real time.', score: 2 },
        { text: 'Key operational KPIs are tracked but cross-system RCA takes hours.', score: 3 },
        { text: 'Real-time monitoring of grid events, metering, and billing with near-instant alerting on failures.', score: 4 },
        { text: 'Full operational transaction observability — SCADA, OMS, billing, and metering linked to regulatory SLAs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When an outage management system failure, SCADA integration error, or billing processing degradation occurs, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving a grid control system outage, OMS delay, or smart metering data collection failure.',
      options: [
        { text: 'Several hours to days — OT and IT teams coordinate manually across siloed systems.', score: 1 },
        { text: '1–4 hours — some tooling exists but cross-system correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most OT and IT tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from operational event to system root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to grid SLAs and regulatory reliability indices.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can operations leadership and commercial teams see real-time health of key business processes — such as outage resolution SLAs, billing run completion, or metering data freshness?',
      hint: 'Think of grid operations NOC dashboards, commercial billing health views, or field operations management centres.',
      options: [
        { text: 'No — leadership receives periodic operational reports only.', score: 1 },
        { text: 'Some metrics available in BI tools but they lag by hours.', score: 2 },
        { text: 'Near-real-time dashboards exist for operations teams; leadership does not have direct access.', score: 3 },
        { text: 'Operations leadership has live dashboards with alerts on grid, billing, and metering KPIs.', score: 4 },
        { text: 'A unified utility operations platform — grid, commercial, and regulatory teams share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive health monitoring of critical operational systems — SCADA, OMS, billing, and smart metering infrastructure?',
      hint: 'Proactive health checks detect processing failures before they cascade to consumer billing errors or regulatory reporting gaps.',
      options: [
        { text: 'No proactive monitoring — failures are discovered through field reports or billing exceptions.', score: 1 },
        { text: 'Periodic availability checks on key servers; no transaction-level health monitoring.', score: 2 },
        { text: 'Key system health metrics monitored; end-to-end transaction health is not proactively tested.', score: 3 },
        { text: 'Proactive health checks across SCADA, OMS, and billing with auto-escalation on failure.', score: 4 },
        { text: 'Continuous end-to-end operational monitoring with regulatory reliability impact scoring.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to regulatory reliability indices such as SAIDI and SAIFI, billing accuracy SLAs, or smart meter data quality targets set by your national energy regulator?',
      hint: 'For example, do you track "meter read success rate vs. regulatory target" or "outage duration contribution to reliability indices" as operational KPIs?',
      options: [
        { text: 'No — IT metrics and regulatory reliability indices are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — operations managers compile regulatory KPI reports manually.', score: 2 },
        { text: 'Regulatory KPIs are tracked in a compliance tool; operational observability is separate.', score: 3 },
        { text: 'Most observability KPIs map to regulatory targets and are reviewed jointly by operations and compliance.', score: 4 },
        { text: 'Full alignment — observability directly feeds regulatory submissions, reliability index reporting, and tariff proceedings.', score: 5 }
      ]
    }
  ],

  // ── MANUFACTURING & AUTOMOTIVE ────────────────────────────────────────────

  manufacturing: [
    {
      id: 'txn1',
      text: 'How do you monitor critical manufacturing transactions — such as production orders, quality inspection results, ERP/MES work order completions, and supply chain events?',
      hint: 'How does your operations team know when a production line has stopped, a quality hold has not been processed, or an ERP transaction affecting delivery commitments has failed?',
      options: [
        { text: 'We find out through production line alerts, supervisor escalations, or daily shift reports.', score: 1 },
        { text: 'We monitor system availability but transaction-level health is not tracked in real time.', score: 2 },
        { text: 'Key production KPIs such as OEE are tracked but cross-system RCA takes hours.', score: 3 },
        { text: 'Real-time production transaction monitoring across ERP, MES, and SCADA with near-instant alerting on failures.', score: 4 },
        { text: 'Full manufacturing transaction observability — ERP, MES, SCADA, and QMS metrics linked to delivery and quality SLAs with automated triage.', score: 5 }
      ]
    },
    {
      id: 'txn2',
      text: 'When an ERP outage, MES communication failure, or SCADA connectivity issue disrupts production, how quickly can your team identify root cause?',
      hint: 'Think of your last major incident involving an SAP/Oracle downtime, MES integration failure, or PLC/SCADA connectivity loss.',
      options: [
        { text: 'Several hours — OT and IT teams debug manually across siloed systems.', score: 1 },
        { text: '1–4 hours — some tooling exists but cross-domain correlation is manual.', score: 2 },
        { text: '30–60 minutes — correlated dashboards exist across most IT and OT tiers.', score: 3 },
        { text: 'Under 15 minutes — automated correlation from production impact to system root cause.', score: 4 },
        { text: 'Under 5 minutes — ML-driven anomaly detection linked to OEE and delivery SLA impact.', score: 5 }
      ]
    },
    {
      id: 'txn3',
      text: 'Can plant managers, supply chain leads, and quality heads see real-time manufacturing health — such as OEE, production order completion rates, quality rejection volumes, or supplier delivery status?',
      hint: 'Think of manufacturing operations dashboards, plant NOCs, or supply chain control towers.',
      options: [
        { text: 'No — leadership receives shift reports or daily production summaries only.', score: 1 },
        { text: 'Some production KPIs available in MES dashboards but not accessible to supply chain or quality leadership.', score: 2 },
        { text: 'Near-real-time dashboards exist for operations teams; supply chain and quality do not have direct access.', score: 3 },
        { text: 'Plant managers and functional leads have live dashboards with alerts on production, quality, and supply KPIs.', score: 4 },
        { text: 'A unified manufacturing intelligence platform — operations, supply chain, quality, and commercial share one live view.', score: 5 }
      ]
    },
    {
      id: 'txn4',
      text: 'How mature is your proactive monitoring of critical manufacturing systems — ERP, MES, SCADA, quality management, and supply chain platforms?',
      hint: 'Proactive health checks detect system failures before they halt production lines or cause missed delivery commitments.',
      options: [
        { text: 'No proactive monitoring — failures are discovered when production stops.', score: 1 },
        { text: 'Periodic availability checks on key servers; no transaction or process health monitoring.', score: 2 },
        { text: 'Key system health metrics monitored; end-to-end production transaction health is not proactively tracked.', score: 3 },
        { text: 'Proactive health monitoring across ERP, MES, and SCADA with auto-escalation on failure.', score: 4 },
        { text: 'Continuous end-to-end operational health monitoring with OEE and delivery commitment impact scoring.', score: 5 }
      ]
    },
    {
      id: 'txn5',
      text: 'Are your observability KPIs aligned to OEE targets, on-time delivery SLAs, quality rejection rate thresholds, or customer schedule adherence commitments?',
      hint: 'For example, do you track "ERP transaction processing latency vs. production schedule SLA" or "MES downtime impact on OEE" as operational business metrics?',
      options: [
        { text: 'No — IT system metrics and production KPIs are tracked in separate systems.', score: 1 },
        { text: 'Informal alignment — IT teams brief plant management during major system outages.', score: 2 },
        { text: 'Uptime SLAs for key systems are tracked; production impact is calculated retrospectively.', score: 3 },
        { text: 'Most observability KPIs map to OEE and delivery commitments; reviewed jointly by IT and plant management.', score: 4 },
        { text: 'Full alignment — observability directly drives incident prioritisation, capacity planning, and customer delivery SLA reporting.', score: 5 }
      ]
    }
  ]

};


// ─── DOMAIN 5: Compliance & Audit Readiness — sector × country variants ───────

var compVariants = {

  // ── BFSI REGULATED ────────────────────────────────────────────────────────

  bfsi_regulated: [
    {
      id: 'comp1',
      text: 'How does your organisation currently meet RBI / SEBI log retention mandates?',
      hint: 'RBI master directions and SEBI regulations mandate specific retention periods for IT and audit logs.',
      options: [
        { text: 'We are not fully aware of what is mandated or whether we comply.', score: 1 },
        { text: 'We have a policy on paper; actual implementation is partial.', score: 2 },
        { text: 'We meet the minimum retention requirement but query and audit capabilities are limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and evidence generation capability.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand regulatory reporting.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your logs stored in a tamper-proof, write-once manner to support forensic audit?',
      hint: 'WORM (Write Once Read Many) storage is increasingly expected by RBI, SEBI, and internal audit.',
      options: [
        { text: 'Logs are on standard storage — they can be modified or deleted.', score: 1 },
        { text: 'Some log files archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Critical security logs on WORM storage; general IT logs are not.', score: 3 },
        { text: 'Most IT and security logs on WORM or immutable storage with access audit trails.', score: 4 },
        { text: 'All regulatory-relevant logs on certified immutable storage with cryptographic integrity checks.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a regulatory IT audit or forensic investigation request?',
      hint: 'For example, RBI asks for all user access logs for a specific system covering the past 6 months.',
      options: [
        { text: 'Weeks — logs are distributed, unstructured, and difficult to extract.', score: 1 },
        { text: 'Several days — we can find the data but extraction is manual.', score: 2 },
        { text: '24–48 hours with significant manual effort from the IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package logs for auditors.', score: 4 },
        { text: 'Within hours — automated audit-pack generation with a full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can view, query, or export sensitive log data?',
      hint: 'Log data often contains PII, transaction details, and credentials — RBI and SEBI expect controlled access.',
      options: [
        { text: 'No — log access is not controlled; any team member can access raw logs.', score: 1 },
        { text: 'Basic access control by team; for example only ops can access log servers.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of who accessed or exported which logs.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and real-time access alerts.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your data residency and log egress policy defined and enforced — especially for cloud workloads?',
      hint: 'RBI mandates that payment and financial data remain on Indian soil. Log data may be in scope.',
      options: [
        { text: 'No formal data residency policy exists for logs.', score: 1 },
        { text: 'Policy exists on paper; actual log flow has not been formally audited.', score: 2 },
        { text: 'On-premise storage for critical systems; cloud logs may egress overseas.', score: 3 },
        { text: 'All logs stored on-premise or in Indian data centres; residency audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all logs ingested, processed, and stored within the organisation perimeter.', score: 5 }
      ]
    }
  ],

  bfsi_regulated_gcc: [
    {
      id: 'comp1',
      text: 'How does your organisation meet CBUAE Information Assurance Regulation (IAR) or SAMA Cybersecurity Framework log retention and audit requirements?',
      hint: 'CBUAE IAR and SAMA CSF mandate specific retention periods, integrity controls, and auditability for IT and security event logs.',
      options: [
        { text: 'We are not fully aware of what is mandated or whether we comply.', score: 1 },
        { text: 'We have a policy on paper; actual implementation is partial.', score: 2 },
        { text: 'We meet minimum retention requirements but query and audit capabilities are limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and on-demand evidence generation.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand CBUAE/SAMA regulatory reporting.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your transaction and system logs stored in a tamper-proof, write-once manner as required for regulatory forensic audit?',
      hint: 'CBUAE IAR and SAMA CSF require demonstrable evidence that logs cannot be altered by insiders or system administrators.',
      options: [
        { text: 'Logs are on standard storage — they can be modified or deleted.', score: 1 },
        { text: 'Some log files archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Critical security logs on WORM storage; operational logs are not.', score: 3 },
        { text: 'Most IT and security logs on WORM or immutable storage with access audit trails.', score: 4 },
        { text: 'All regulatory-relevant logs on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a CBUAE, DFSA, or SAMA audit or forensic investigation request for system logs?',
      hint: 'For example, CBUAE requests all privileged user access logs for a specific system covering the past 12 months.',
      options: [
        { text: 'Weeks — logs are distributed, unstructured, and difficult to extract.', score: 1 },
        { text: 'Several days — we can find the data but extraction is manual.', score: 2 },
        { text: '24–48 hours with significant manual effort from the IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package logs for regulators.', score: 4 },
        { text: 'Within hours — automated audit-pack generation with full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can view, query, or export logs containing customer financial and personal data?',
      hint: 'UAE Personal Data Protection Law (PDPL) and CBUAE IAR require controlled, auditable access to sensitive financial and personal data in logs.',
      options: [
        { text: 'No — log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access control on log systems.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and real-time access alerts for sensitive data.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your data residency policy compliant with UAE or KSA data sovereignty requirements for financial data and logs?',
      hint: 'UAE PDPL and CBUAE/SAMA requirements mandate that customer financial data be processed and stored within the respective country\'s jurisdiction.',
      options: [
        { text: 'No formal data residency policy for logs.', score: 1 },
        { text: 'Policy exists on paper; actual data flows have not been formally audited.', score: 2 },
        { text: 'Core banking data is on-premise or in-country; some operational logs may flow to overseas cloud.', score: 3 },
        { text: 'All regulated data stored within UAE/KSA jurisdiction; residency audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all logs ingested, processed, and stored within the country perimeter.', score: 5 }
      ]
    }
  ],

  bfsi_regulated_intl: [
    {
      id: 'comp1',
      text: 'How does your organisation meet applicable regulatory log retention requirements — for example MAS Notice 644, FCA/PRA technology resilience rules, APRA CPS 234, or FFIEC guidance?',
      hint: 'Financial regulators across most jurisdictions mandate specific retention periods, integrity controls, and audit access capabilities for IT and security event logs.',
      options: [
        { text: 'We are not fully aware of what is mandated or whether we comply.', score: 1 },
        { text: 'We have a policy on paper; actual implementation is partial.', score: 2 },
        { text: 'We meet minimum retention requirements but query and audit capabilities are limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and on-demand evidence generation.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand regulatory evidence packaging.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your logs stored in a tamper-proof manner to support regulatory forensic audit and incident investigation?',
      hint: 'MAS TRM, FCA and PRA operational resilience frameworks, and APRA CPS 234 require demonstrable evidence that logs cannot be altered by insiders.',
      options: [
        { text: 'Logs are on standard storage — they can be modified or deleted.', score: 1 },
        { text: 'Some log files archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Critical security logs on WORM storage; operational logs are not.', score: 3 },
        { text: 'Most IT and security logs on WORM or immutable storage with access audit trails.', score: 4 },
        { text: 'All regulatory-relevant logs on certified immutable storage with cryptographic integrity checks.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a forensic investigation or audit request from your financial regulator — MAS, FCA, APRA, OCC, or equivalent?',
      hint: 'Regulators can request specific system logs with defined response windows — often 24 to 72 hours for material incidents.',
      options: [
        { text: 'Weeks — logs are distributed, unstructured, and difficult to extract.', score: 1 },
        { text: 'Several days — we can find the data but extraction is manual.', score: 2 },
        { text: '24–48 hours with significant manual effort from the IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package logs for auditors.', score: 4 },
        { text: 'Within hours — automated audit-pack generation with a full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have fine-grained access controls on who can view, query, or export logs containing customer financial data?',
      hint: 'GDPR (EU/UK), PDPA (Singapore), Privacy Act (Australia), or applicable data protection law requires controlled and auditable access to personal data in logs.',
      options: [
        { text: 'No — log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access control on log systems.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and real-time access alerts for sensitive data.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your log storage compliant with applicable data localisation requirements — such as MAS data residency rules, APRA\'s data sovereignty guidance, or UK GDPR data transfer restrictions?',
      hint: 'Financial regulators in several jurisdictions require that specific categories of customer and transaction data — including audit logs — remain within the licensed territory.',
      options: [
        { text: 'No formal data residency policy exists for logs.', score: 1 },
        { text: 'Policy exists on paper; actual log storage locations have not been formally audited.', score: 2 },
        { text: 'Core financial data is localised; log residency has not been fully mapped.', score: 3 },
        { text: 'All regulated log data stored in compliant regions; residency policy audited at least annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all logs ingested, processed, and stored within the licensed jurisdiction.', score: 5 }
      ]
    }
  ],

  // ── PAYMENTS ──────────────────────────────────────────────────────────────

  payments: [
    {
      id: 'comp1',
      text: 'How does your organisation meet NPCI / RBI requirements for payment system log retention and audit readiness?',
      hint: 'Payment system operators face specific log mandates from NPCI operating guidelines and RBI payment system directions.',
      options: [
        { text: 'We are not fully clear on what is mandated or whether we currently comply.', score: 1 },
        { text: 'We have a compliance policy on paper; actual log retention coverage is partial.', score: 2 },
        { text: 'We meet minimum retention requirements but our query and evidence generation capability is limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and on-demand evidence generation.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand regulatory and settlement audit packs.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your payment transaction logs and settlement reconciliation records stored in a tamper-proof manner?',
      hint: 'Dispute resolution and regulatory audit require that transaction records cannot be altered retroactively.',
      options: [
        { text: 'Transaction logs are on standard storage and can be modified.', score: 1 },
        { text: 'Some transaction records are archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Settlement records on WORM storage; operational transaction logs are not.', score: 3 },
        { text: 'Most transaction and settlement logs on immutable storage with access audit trails.', score: 4 },
        { text: 'All payment-relevant logs on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you produce a complete audit trail for a specific disputed payment transaction or settlement cycle?',
      hint: 'For example, NPCI or a regulator requests the full log trace for a disputed UPI transaction from 3 months ago.',
      options: [
        { text: 'Weeks — data is spread across multiple systems and hard to correlate.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across teams.', score: 2 },
        { text: '24–48 hours with IT team involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package the required evidence.', score: 4 },
        { text: 'Within hours — automated dispute and audit-pack generation with chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can query or export payment transaction log data?',
      hint: 'Payment logs contain sensitive financial data and are subject to PCI-DSS and RBI access control requirements.',
      options: [
        { text: 'No — payment log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access control on log systems.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust access with MFA, just-in-time provisioning, and real-time access alerts for payment data.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is cardholder and payment data storage compliant with PCI-DSS data residency and processing requirements?',
      hint: 'PCI-DSS and RBI payment system rules govern where cardholder and transaction data may be stored and processed.',
      options: [
        { text: 'No formal data residency or PCI scope definition for payment logs.', score: 1 },
        { text: 'Policy exists on paper; actual data flow has not been formally audited against PCI-DSS.', score: 2 },
        { text: 'Core payment processing is on-premise; some ancillary logs may flow to cloud or overseas.', score: 3 },
        { text: 'All in-scope payment data stored within compliant infrastructure; residency audited at least annually.', score: 4 },
        { text: 'Zero data egress enforced technically with continuous compliance monitoring and annual PCI-DSS certification.', score: 5 }
      ]
    }
  ],

  payments_intl: [
    {
      id: 'comp1',
      text: 'How does your organisation meet PCI-DSS v4.0 Requirement 10 log retention controls, SWIFT Customer Security Programme (CSP), or applicable local payment regulator requirements?',
      hint: 'PCI-DSS mandates 12-month log retention with automated audit trails, integrity controls, and alerting for all in-scope payment processing systems.',
      options: [
        { text: 'We are not fully clear on what is mandated or whether we currently comply.', score: 1 },
        { text: 'We have a compliance policy on paper; actual log retention coverage is partial.', score: 2 },
        { text: 'We meet minimum retention requirements but query and evidence generation capability is limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and on-demand evidence generation.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand PCI/scheme audit packs.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your payment transaction logs stored in a tamper-proof manner aligned to PCI-DSS Requirement 10.5?',
      hint: 'PCI-DSS Requirement 10.5 mandates that audit logs be protected from modification or deletion — even by system administrators.',
      options: [
        { text: 'Transaction logs are on standard storage and can be modified.', score: 1 },
        { text: 'Some transaction records archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Settlement records on WORM storage; operational transaction logs are not.', score: 3 },
        { text: 'Most transaction and settlement logs on immutable storage with access audit trails.', score: 4 },
        { text: 'All in-scope payment logs on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you produce a complete transaction audit trail for a disputed payment, a card network chargeback investigation, or a real-time payment scheme audit?',
      hint: 'For example, Visa or your local payment scheme operator requests the full log trace for a disputed transaction from 6 months ago.',
      options: [
        { text: 'Weeks — data is spread across multiple systems and hard to correlate.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across teams.', score: 2 },
        { text: '24–48 hours with IT team involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package the required evidence.', score: 4 },
        { text: 'Within hours — automated dispute and audit-pack generation with chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can view or export payment log data, aligned to PCI-DSS Requirement 10.2 and applicable data protection law?',
      hint: 'PCI-DSS restricts access to cardholder data environment logs; GDPR, CCPA, or local data protection law may add further requirements.',
      options: [
        { text: 'No — payment log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access control on log systems.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust access with MFA, just-in-time provisioning, and real-time alerts for cardholder data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your payment data and log storage compliant with applicable data residency requirements — such as GDPR data transfer rules, PDPA obligations, or card scheme data handling requirements?',
      hint: 'Several jurisdictions and payment schemes require that transaction records and audit logs be stored within defined geographic boundaries.',
      options: [
        { text: 'No formal data residency or scope definition for payment logs.', score: 1 },
        { text: 'Policy exists on paper; actual data flow has not been formally audited.', score: 2 },
        { text: 'Core payment processing is within the required boundary; some ancillary logs may egress.', score: 3 },
        { text: 'All in-scope payment data stored within compliant regions; residency audited at least annually.', score: 4 },
        { text: 'Zero data egress enforced technically with continuous compliance monitoring and annual certification.', score: 5 }
      ]
    }
  ],

  // ── GOVERNMENT ────────────────────────────────────────────────────────────

  government: [
    {
      id: 'comp1',
      text: 'How does your organisation meet MeitY / NIC requirements for government system log retention and audit readiness?',
      hint: 'Government IT systems are subject to NIC security guidelines, CERT-In directives, and departmental audit requirements.',
      options: [
        { text: 'We are not fully clear on what is mandated or whether we currently comply.', score: 1 },
        { text: 'We have a log retention policy on paper; actual implementation is partial across departments.', score: 2 },
        { text: 'We meet the minimum retention requirement but our evidence generation capability is limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and evidence generation for CAG and internal audit.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand audit pack generation for all statutory requirements.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your system and access logs stored in a tamper-evident manner to support government audit and CERT-In directives?',
      hint: 'CERT-In log retention directives (2022) require tamper-proof storage for ICT infrastructure logs.',
      options: [
        { text: 'Logs are on standard storage and can be modified or deleted.', score: 1 },
        { text: 'Some logs archived in read-only mode but not formally WORM or tamper-evident.', score: 2 },
        { text: 'Security and access logs on tamper-evident storage; operational logs are not.', score: 3 },
        { text: 'Most government system logs on immutable storage aligned to CERT-In requirements.', score: 4 },
        { text: 'All in-scope logs on certified immutable storage with cryptographic integrity checks and chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a CAG audit, CERT-In directive, or RTI request for system access and activity logs?',
      hint: 'Government entities can receive audit requests with short response timelines from statutory bodies.',
      options: [
        { text: 'Weeks — logs are distributed across departments and difficult to consolidate.', score: 1 },
        { text: 'Several days — possible but requires significant manual co-ordination across IT teams.', score: 2 },
        { text: '24–48 hours with significant effort from the central IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package logs for auditors.', score: 4 },
        { text: 'Within hours — automated audit pack generation with full chain of custody for statutory submissions.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can view, query, or export logs containing citizen data?',
      hint: 'Government systems handling Aadhaar, PAN, health, or welfare data are subject to strict access control requirements under the DPDP Act and departmental policies.',
      options: [
        { text: 'No — log access is not formally controlled within the department.', score: 1 },
        { text: 'Basic team-level access; for example only IT staff can access log servers.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and automated alerts for sensitive data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your government data processing and storage compliant with NIC cloud policy and data localisation requirements?',
      hint: 'MeitY policy mandates that government data — including logs — be stored within India on approved cloud or on-premise infrastructure.',
      options: [
        { text: 'No formal data localisation policy for log data.', score: 1 },
        { text: 'Policy exists on paper; actual log storage locations have not been formally audited.', score: 2 },
        { text: 'Core data is on NIC or approved cloud; some log data may reside on non-compliant infrastructure.', score: 3 },
        { text: 'All government data and logs on NIC-approved infrastructure within India; audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all logs ingested, processed, and stored within approved government infrastructure.', score: 5 }
      ]
    }
  ],

  government_intl: [
    {
      id: 'comp1',
      text: 'How does your organisation meet applicable government IT audit and log retention requirements — such as NIST SP 800-92, Cyber Essentials Plus, IRAP, or your national cybersecurity framework mandates?',
      hint: 'Government IT systems are subject to national security and audit frameworks that mandate retention periods, integrity controls, and audit evidence generation.',
      options: [
        { text: 'We are not fully clear on what is mandated or whether we currently comply.', score: 1 },
        { text: 'We have a log retention policy on paper; actual implementation is partial across departments.', score: 2 },
        { text: 'We meet minimum retention requirements but evidence generation capability is limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and evidence generation capability.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand audit pack generation for all statutory requirements.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your system and access logs stored in a tamper-evident manner to support internal and external statutory audit?',
      hint: 'Most government security frameworks — NIST, Cyber Essentials, ISM (Australia), CSP (Singapore) — require that logs cannot be altered or deleted by insiders.',
      options: [
        { text: 'Logs are on standard storage and can be modified or deleted.', score: 1 },
        { text: 'Some logs archived in read-only mode but not formally WORM or tamper-evident.', score: 2 },
        { text: 'Security and access logs on tamper-evident storage; operational logs are not.', score: 3 },
        { text: 'Most government system logs on immutable storage aligned to the applicable national security framework.', score: 4 },
        { text: 'All in-scope logs on certified immutable storage with cryptographic integrity checks and chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a statutory audit, parliamentary or congressional inquiry, or Freedom of Information / open records request requiring system activity logs?',
      hint: 'Government entities receive audit and FOI/FOIA/OIA requests with defined response timelines — typically 20 to 30 business days.',
      options: [
        { text: 'Weeks — logs are distributed across departments and difficult to consolidate.', score: 1 },
        { text: 'Several days — possible but requires significant manual co-ordination across IT teams.', score: 2 },
        { text: '24–48 hours with significant effort from the central IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package logs for auditors or the requesting authority.', score: 4 },
        { text: 'Within hours — automated audit pack generation with full chain of custody for statutory submissions.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can view, query, or export logs containing citizen personal data?',
      hint: 'GDPR, CCPA, PDPA (Singapore), Privacy Act (Australia), or applicable national data protection legislation requires controlled and audited access to personal data in logs.',
      options: [
        { text: 'No — log access is not formally controlled within the department.', score: 1 },
        { text: 'Basic team-level access; for example only IT staff can access log servers.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and automated alerts for sensitive citizen data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your government data processing and storage compliant with national sovereignty requirements and approved cloud security policies?',
      hint: 'Most government jurisdictions mandate that sensitive citizen data and audit logs be on approved sovereign infrastructure — UK G-Cloud, US FedRAMP, AU IRAP, SG GCC, UAE TRA-certified.',
      options: [
        { text: 'No formal data sovereignty or cloud security policy for log data.', score: 1 },
        { text: 'Policy exists on paper; actual log storage locations have not been formally audited.', score: 2 },
        { text: 'Core systems are on approved infrastructure; some log data may reside elsewhere.', score: 3 },
        { text: 'All government data and logs on sovereign or approved cloud infrastructure; audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all logs ingested, processed, and stored within approved sovereign infrastructure.', score: 5 }
      ]
    }
  ],

  // ── TECHNOLOGY (country-agnostic) ─────────────────────────────────────────

  technology: [
    {
      id: 'comp1',
      text: 'How does your organisation maintain audit-ready log evidence for SOC 2, ISO 27001, or other applicable security certifications?',
      hint: 'Certification audits require evidence of control effectiveness; log data is often a primary source.',
      options: [
        { text: 'We are not fully clear on what log evidence each certification requires.', score: 1 },
        { text: 'We have log retention policies on paper; evidence collection before audits is largely manual.', score: 2 },
        { text: 'We meet minimum log retention requirements but pulling evidence for audits takes significant effort.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails; evidence packages are prepared within a day.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand audit evidence generation for all certification scopes.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your customer data access logs and system events stored in a tamper-proof manner for compliance and incident forensics?',
      hint: 'SOC 2 Trust Service Criteria and ISO 27001 require evidence that logs cannot be altered by insiders.',
      options: [
        { text: 'Logs are on standard storage and can be modified or deleted.', score: 1 },
        { text: 'Some logs archived in read-only mode but not formally WORM or tamper-evident.', score: 2 },
        { text: 'Security and access logs on tamper-evident storage; application logs are not.', score: 3 },
        { text: 'Most audit-relevant logs on immutable storage with access audit trails.', score: 4 },
        { text: 'All in-scope logs on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a customer audit request, regulatory inquiry, or security incident forensics investigation?',
      hint: 'Enterprise customers increasingly require the right to audit their vendor\'s log controls; regulators can mandate short response windows.',
      options: [
        { text: 'Weeks — log data is distributed and difficult to query across the time range needed.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort from the engineering team.', score: 2 },
        { text: '24–48 hours with IT involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package logs for the requesting party.', score: 4 },
        { text: 'Within hours — automated evidence package generation with full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have fine-grained access controls on who can view, query, or export logs containing customer data?',
      hint: 'Logs may contain personal data, API keys, or sensitive business context — insider access must be controlled and audited.',
      options: [
        { text: 'No — log access is not formally controlled within the engineering team.', score: 1 },
        { text: 'Basic team-level access; for example only SRE or security can access production logs.', score: 2 },
        { text: 'RBAC defined on the log platform but access events are not audited comprehensively.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and automated alerts for sensitive data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your log processing and storage compliant with DPDP Act, GDPR, CCPA, or other applicable data residency requirements?',
      hint: 'If you serve regulated customers or operate in multiple jurisdictions, data localisation of logs may be a contractual or legal requirement.',
      options: [
        { text: 'No formal data residency policy exists for log data.', score: 1 },
        { text: 'Policy exists on paper; actual log storage locations have not been formally audited.', score: 2 },
        { text: 'Core product data is localised; log data residency has not been fully mapped.', score: 3 },
        { text: 'All log data stored in compliant regions; residency policy audited at least annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all logs ingested, processed, and stored within contractually required boundaries.', score: 5 }
      ]
    }
  ],

  // ── RETAIL & E-COMMERCE ───────────────────────────────────────────────────

  retail: [
    {
      id: 'comp1',
      text: 'How does your organisation meet PCI-DSS log retention requirements and DPDP Act obligations for customer transaction and personal data records?',
      hint: 'Retail businesses processing card payments must meet PCI-DSS Requirement 10 (12-month log retention); customer data in logs is governed by the DPDP Act.',
      options: [
        { text: 'We are not fully clear on what is mandated or whether we comply.', score: 1 },
        { text: 'We have a policy on paper; actual log retention coverage is partial.', score: 2 },
        { text: 'We meet minimum PCI-DSS retention but query and evidence generation capability is limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and on-demand evidence generation.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand PCI-DSS and DPDP audit evidence.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your POS transaction logs, payment records, and customer data access logs stored in a tamper-proof manner?',
      hint: 'PCI-DSS Requirement 10.5 mandates that audit logs cannot be modified; DPDP Act requires demonstrable access controls on personal data.',
      options: [
        { text: 'Transaction logs are on standard storage and can be modified.', score: 1 },
        { text: 'Some records archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Payment system logs on WORM storage; customer data access logs are not.', score: 3 },
        { text: 'Most payment and customer data logs on immutable storage with access audit trails.', score: 4 },
        { text: 'All in-scope logs on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a payment dispute investigation, consumer forum order, or DPDP data principal request requiring transaction or personal data logs?',
      hint: 'Payment networks require chargeback evidence within days; DPDP Act mandates response to data principal requests within defined timelines.',
      options: [
        { text: 'Weeks — data is spread across systems and hard to correlate.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across teams.', score: 2 },
        { text: '24–48 hours with IT involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package the required evidence.', score: 4 },
        { text: 'Within hours — automated evidence package generation with full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can access customer order data, payment logs, and loyalty programme records?',
      hint: 'Customer purchase history and payment data constitute personal data under the DPDP Act — access must be controlled and auditable.',
      options: [
        { text: 'No — log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access; for example only IT can access production logs.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and customer data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and automated alerts for customer data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your customer and transaction data storage compliant with DPDP Act data localisation requirements and PCI-DSS cardholder data handling standards?',
      hint: 'The DPDP Act may impose data localisation requirements; PCI-DSS governs where cardholder data may be stored and processed.',
      options: [
        { text: 'No formal data residency or PCI scope definition for customer and payment logs.', score: 1 },
        { text: 'Policy exists on paper; actual data flows have not been formally audited.', score: 2 },
        { text: 'Core payment processing is on-premise or in-country; some customer logs may flow to overseas cloud.', score: 3 },
        { text: 'All in-scope customer and payment data stored within compliant infrastructure; residency audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically with continuous compliance monitoring and PCI-DSS certification.', score: 5 }
      ]
    }
  ],

  retail_intl: [
    {
      id: 'comp1',
      text: 'How does your organisation meet PCI-DSS v4.0 log retention requirements and applicable data protection law (GDPR, CCPA, or equivalent) for customer transaction records?',
      hint: 'Retail businesses processing card payments must meet PCI-DSS Requirement 10; customer personal data in logs is governed by GDPR, CCPA, or applicable law.',
      options: [
        { text: 'We are not fully clear on what is mandated or whether we comply.', score: 1 },
        { text: 'We have a policy on paper; actual log retention coverage is partial.', score: 2 },
        { text: 'We meet minimum PCI-DSS retention but query and audit evidence capability is limited.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails and on-demand evidence generation.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand PCI-DSS and data protection audit evidence.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your POS transaction logs, payment records, and customer data access logs stored in a tamper-proof manner?',
      hint: 'PCI-DSS Requirement 10.5 mandates that audit logs cannot be modified; GDPR and CCPA require demonstrable access controls on personal data.',
      options: [
        { text: 'Transaction logs are on standard storage and can be modified.', score: 1 },
        { text: 'Some records archived in read-only mode but not formally WORM-compliant.', score: 2 },
        { text: 'Payment system logs on WORM storage; customer data access logs are not.', score: 3 },
        { text: 'Most payment and customer data logs on immutable storage with access audit trails.', score: 4 },
        { text: 'All in-scope logs on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a payment dispute investigation, data protection authority inquiry, or consumer data access request requiring transaction or personal data logs?',
      hint: 'Card schemes require chargeback evidence within days; GDPR and CCPA mandate responses to data subject/consumer requests within defined statutory windows.',
      options: [
        { text: 'Weeks — data is spread across systems and hard to correlate.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort.', score: 2 },
        { text: '24–48 hours with IT involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package the required evidence.', score: 4 },
        { text: 'Within hours — automated evidence package generation with full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on who can access customer order data, payment logs, and loyalty programme records?',
      hint: 'GDPR, CCPA, or applicable data protection law classifies customer purchase history and payment data as personal data requiring controlled access.',
      options: [
        { text: 'No — log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access; for example only IT can access production logs.', score: 2 },
        { text: 'RBAC defined on the log platform but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all log access and customer data exports.', score: 4 },
        { text: 'Zero-trust log access with MFA, just-in-time provisioning, and automated alerts for customer data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your customer and transaction data storage compliant with applicable data residency requirements — such as GDPR data transfer rules, CCPA, or PCI-DSS cardholder data handling standards?',
      hint: 'Data protection law and PCI-DSS jointly govern where customer personal data and cardholder information may be stored, processed, and transferred.',
      options: [
        { text: 'No formal data residency or PCI scope definition for customer and payment logs.', score: 1 },
        { text: 'Policy exists on paper; actual data flows have not been formally audited.', score: 2 },
        { text: 'Core payment processing is within the required boundary; some customer logs may egress.', score: 3 },
        { text: 'All in-scope customer and payment data stored within compliant regions; residency audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically with continuous compliance monitoring and PCI-DSS certification.', score: 5 }
      ]
    }
  ],

  // ── TELECOM ───────────────────────────────────────────────────────────────

  telecom: [
    {
      id: 'comp1',
      text: 'How does your organisation meet DoT licensing conditions and TRAI regulations for CDR retention, lawful interception readiness, and CERT-In log audit compliance?',
      hint: 'DoT licensing mandates CDR retention for 1 year; CERT-In directives require tamper-proof log storage for ICT infrastructure; TRAI QoS requires specific records.',
      options: [
        { text: 'We are not fully clear on all mandates or whether we currently comply.', score: 1 },
        { text: 'We have compliance policies on paper; actual CDR and log retention coverage is partial.', score: 2 },
        { text: 'We meet minimum CDR retention requirements but audit and evidence generation capability is limited.', score: 3 },
        { text: 'Compliant CDR and log retention with access-controlled audit trails and lawful interception readiness.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand DoT/TRAI/CERT-In audit packs.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your CDRs, network event logs, and lawful interception records stored in a tamper-proof, access-controlled manner?',
      hint: 'DoT licensing conditions and India\'s lawful interception framework require that CDRs and interception records are immutable and available to authorised agencies on demand.',
      options: [
        { text: 'CDRs are on standard storage and can be modified or deleted.', score: 1 },
        { text: 'CDRs archived in read-only mode but not formally tamper-evident or cryptographically secured.', score: 2 },
        { text: 'CDRs on WORM storage; network event and operations logs are not.', score: 3 },
        { text: 'CDRs and key operational logs on immutable storage with strict access controls and audit trails.', score: 4 },
        { text: 'All DoT-mandated records on certified immutable storage with cryptographic integrity and chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a DoT licence audit, TRAI compliance check, or a court or agency order for subscriber and traffic data?',
      hint: 'Lawful interception requests under the Indian Telegraph Act and IT Act must be fulfilled within hours; DoT licence audits require rapid evidence production.',
      options: [
        { text: 'Weeks — CDRs and logs are distributed and difficult to extract at scale.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across network and IT teams.', score: 2 },
        { text: '24–48 hours with IT team involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package CDRs and logs for the requesting authority.', score: 4 },
        { text: 'Within hours — automated audit-pack and lawful interception evidence generation with full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have strict role-based access controls on CDRs, subscriber data, and network management logs?',
      hint: 'Subscriber data constitutes personal data under the DPDP Act; CDRs and location data carry additional sensitivity under DoT regulations and the Telecom Act.',
      options: [
        { text: 'No — CDR and subscriber data access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access; for example only NOC staff can access CDR systems.', score: 2 },
        { text: 'RBAC defined on CDR and log platforms but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all CDR and subscriber data access.', score: 4 },
        { text: 'Zero-trust access with MFA, just-in-time provisioning, and automated alerts for sensitive subscriber data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your subscriber data, CDR storage, and network management data compliant with data localisation requirements under the Indian Telecom Act and DPDP Act?',
      hint: 'Indian regulatory framework requires that subscriber data and CDRs remain within India; network management and diagnostic data may have additional localisation requirements.',
      options: [
        { text: 'No formal data localisation policy for CDRs and subscriber data.', score: 1 },
        { text: 'Policy exists on paper; actual data storage locations have not been formally audited.', score: 2 },
        { text: 'Core CDR storage is within India; some network management data may flow to overseas cloud or vendor systems.', score: 3 },
        { text: 'All DoT-mandated subscriber and CDR data stored within India; residency audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all subscriber data and CDRs ingested, processed, and stored within Indian jurisdiction.', score: 5 }
      ]
    }
  ],

  telecom_intl: [
    {
      id: 'comp1',
      text: 'How does your organisation meet applicable telecom regulatory log retention requirements — including data retention directives, lawful interception obligations, and national regulator mandates (Ofcom, FCC, BEREC, TRA)?',
      hint: 'Telecom operators face lawful interception and data retention laws in each operating jurisdiction, plus network security log requirements from the national telecom regulator.',
      options: [
        { text: 'We are not fully clear on all mandates or whether we currently comply.', score: 1 },
        { text: 'We have compliance policies on paper; actual CDR and log retention coverage is partial.', score: 2 },
        { text: 'We meet minimum CDR retention requirements but audit evidence generation capability is limited.', score: 3 },
        { text: 'Compliant CDR and log retention with access-controlled audit trails and lawful interception readiness.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand regulator and law enforcement audit packs.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your CDRs, network event logs, and lawful interception records stored in a tamper-proof, access-controlled manner?',
      hint: 'Lawful interception legislation and national data retention laws require that CDRs and interception records cannot be altered and are available to authorised agencies on demand.',
      options: [
        { text: 'CDRs are on standard storage and can be modified or deleted.', score: 1 },
        { text: 'CDRs archived in read-only mode but not formally tamper-evident.', score: 2 },
        { text: 'CDRs on WORM storage; network event and operations logs are not.', score: 3 },
        { text: 'CDRs and key operational logs on immutable storage with strict access controls and audit trails.', score: 4 },
        { text: 'All legally mandated records on certified immutable storage with cryptographic integrity and chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a regulator audit, network security directive, or a law enforcement or judicial order for subscriber and traffic data?',
      hint: 'Telecom operators face legal obligations to respond to lawful requests — often within hours for urgent requests, days for standard requests — under national data retention law.',
      options: [
        { text: 'Weeks — CDRs and logs are distributed and difficult to extract at scale.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort.', score: 2 },
        { text: '24–48 hours with IT team involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package CDRs and logs for the requesting authority.', score: 4 },
        { text: 'Within hours — automated audit-pack and lawful interception evidence generation with full chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have strict role-based access controls on CDRs, subscriber data, and network management logs?',
      hint: 'GDPR, ePrivacy Directive, CCPA, or applicable data protection law places strict obligations on how subscriber data and traffic metadata is accessed, processed, and retained.',
      options: [
        { text: 'No — CDR and subscriber data access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access; for example only NOC staff can access CDR systems.', score: 2 },
        { text: 'RBAC defined on CDR and log platforms but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all CDR and subscriber data access.', score: 4 },
        { text: 'Zero-trust access with MFA, just-in-time provisioning, and automated alerts for sensitive subscriber data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your subscriber data, CDR storage, and network management data compliant with applicable data localisation, cross-border transfer restrictions, and national telecom security requirements?',
      hint: 'Several jurisdictions require CDRs and subscriber data to be stored domestically; cross-border transfers may require regulatory approval or specific safeguards under GDPR, ePrivacy, or national telecom law.',
      options: [
        { text: 'No formal data localisation policy for CDRs and subscriber data.', score: 1 },
        { text: 'Policy exists on paper; actual data storage locations have not been formally audited.', score: 2 },
        { text: 'Core CDR storage is within the required jurisdiction; some operational data may flow to overseas systems.', score: 3 },
        { text: 'All legally mandated subscriber and CDR data stored within required jurisdiction; residency audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all subscriber data and CDRs stored within applicable jurisdictional boundaries.', score: 5 }
      ]
    }
  ],

  // ── ENERGY & UTILITIES ────────────────────────────────────────────────────

  energy: [
    {
      id: 'comp1',
      text: 'How does your organisation meet CERC / SERC regulations and CEA guidelines for operational data retention, SCADA log audit, and CERT-In Critical Information Infrastructure (CII) obligations?',
      hint: 'Energy utilities designated as Critical Information Infrastructure face CERT-In log retention and incident reporting mandates; CERC/SERC regulations govern operational data records.',
      options: [
        { text: 'We are not fully clear on all mandates or whether we currently comply.', score: 1 },
        { text: 'We have policies on paper; actual operational and SCADA log retention is partial.', score: 2 },
        { text: 'We meet minimum regulatory retention requirements but audit evidence capability is limited.', score: 3 },
        { text: 'Compliant operational and IT log retention with access-controlled audit trails.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand CERC/SERC/CERT-In audit packs.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your SCADA event logs, metering records, and OT security logs stored in a tamper-evident manner aligned to CERT-In CII requirements?',
      hint: 'CERT-In CII directives require tamper-proof log storage and integrity verification for designated critical infrastructure organisations.',
      options: [
        { text: 'SCADA and OT logs are on standard storage and can be modified.', score: 1 },
        { text: 'Some logs archived in read-only mode but not formally tamper-evident.', score: 2 },
        { text: 'Security and SCADA access logs on immutable storage; operational and metering logs are not.', score: 3 },
        { text: 'Most OT and IT logs on immutable storage aligned to CERT-In requirements.', score: 4 },
        { text: 'All CII-relevant logs on certified immutable storage with cryptographic integrity checks and chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a CERC / SERC regulatory proceeding, CEA inspection, CERT-In incident directive, or consumer forum inquiry requiring operational records?',
      hint: 'Energy regulators and CERT-In can require SCADA, billing, and incident records with short turnaround; consumer disputes may require billing data within days.',
      options: [
        { text: 'Weeks — SCADA and billing data are distributed and difficult to extract.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across OT and IT teams.', score: 2 },
        { text: '24–48 hours with significant effort from the central IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package operational records for regulators.', score: 4 },
        { text: 'Within hours — automated audit pack generation with full chain of custody for regulatory submissions.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on SCADA systems, smart metering data, and consumer billing records?',
      hint: 'Consumer billing and metering data is personal data under the DPDP Act; SCADA access controls are mandated under CERT-In CII and NERC CIP-equivalent frameworks.',
      options: [
        { text: 'No — OT and IT log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access; for example only SCADA operators can access control systems.', score: 2 },
        { text: 'RBAC defined on OT and billing platforms but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all SCADA, metering, and billing data access.', score: 4 },
        { text: 'Zero-trust access across OT and IT with MFA, just-in-time provisioning, and automated alerts for sensitive access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your operational data, smart metering records, and consumer data storage compliant with data localisation requirements under the DPDP Act and CII obligations under the IT Act?',
      hint: 'Organisations designated as Critical Information Infrastructure must meet CERT-In requirements; consumer metering and billing data is subject to DPDP Act localisation requirements.',
      options: [
        { text: 'No formal data localisation policy for operational and consumer data.', score: 1 },
        { text: 'Policy exists on paper; actual data storage locations have not been audited.', score: 2 },
        { text: 'Core SCADA and billing data is within India; some operational analytics may use overseas cloud.', score: 3 },
        { text: 'All CII and consumer data stored within India on compliant infrastructure; audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all operational and consumer data stored within Indian jurisdiction.', score: 5 }
      ]
    }
  ],

  energy_intl: [
    {
      id: 'comp1',
      text: 'How does your organisation meet applicable energy regulatory log retention and audit requirements — such as NERC CIP standards (North America), OFGEM smart meter regulations (UK), or your national grid operator compliance mandates?',
      hint: 'Energy sector organisations face operational data retention obligations from energy regulators, grid operators, and national cybersecurity frameworks (NERC CIP, NIS2, IEC 62351).',
      options: [
        { text: 'We are not fully clear on all mandates or whether we currently comply.', score: 1 },
        { text: 'We have policies on paper; actual operational and SCADA log retention is partial.', score: 2 },
        { text: 'We meet minimum regulatory retention requirements but audit evidence capability is limited.', score: 3 },
        { text: 'Compliant operational and IT log retention with access-controlled audit trails.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand regulatory audit packs.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your SCADA event logs, metering records, and OT security logs stored in a tamper-evident manner aligned to NERC CIP-007, IEC 62351, or equivalent OT security standards?',
      hint: 'NERC CIP-007 and equivalent standards require that OT security and access logs be protected from unauthorised modification and retained for defined periods.',
      options: [
        { text: 'SCADA and OT logs are on standard storage and can be modified.', score: 1 },
        { text: 'Some logs archived in read-only mode but not formally tamper-evident.', score: 2 },
        { text: 'Security and SCADA access logs on immutable storage; operational and metering logs are not.', score: 3 },
        { text: 'Most OT and IT logs on immutable storage aligned to applicable OT security standards.', score: 4 },
        { text: 'All in-scope logs on certified immutable storage with cryptographic integrity checks and chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to a NERC CIP compliance audit, OFGEM inspection, national cyber authority directive, or consumer dispute requiring operational records?',
      hint: 'Energy regulators and national cyber authorities can require SCADA, billing, and incident records with defined response windows; consumer disputes may require billing data within days.',
      options: [
        { text: 'Weeks — SCADA and billing data are distributed and difficult to extract.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across OT and IT teams.', score: 2 },
        { text: '24–48 hours with significant effort from the central IT team.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package operational records for regulators.', score: 4 },
        { text: 'Within hours — automated audit pack generation with full chain of custody for regulatory submissions.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on SCADA systems, smart metering data, and consumer billing records?',
      hint: 'GDPR, CCPA, or applicable data protection law governs consumer metering and billing data; NERC CIP, NIS2, and equivalent OT security standards mandate access controls on industrial control systems.',
      options: [
        { text: 'No — OT and IT log access is not formally controlled.', score: 1 },
        { text: 'Basic team-level access; for example only SCADA operators can access control systems.', score: 2 },
        { text: 'RBAC defined on OT and billing platforms but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all SCADA, metering, and billing data access.', score: 4 },
        { text: 'Zero-trust access across OT and IT with MFA, just-in-time provisioning, and automated alerts for sensitive access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your operational data, smart metering records, and consumer data compliant with applicable data residency, critical infrastructure protection, and smart meter data governance requirements?',
      hint: 'Several jurisdictions require energy sector data — particularly smart meter and grid data — to be stored within national boundaries and protected under critical infrastructure frameworks.',
      options: [
        { text: 'No formal data residency or critical infrastructure data policy for operational data.', score: 1 },
        { text: 'Policy exists on paper; actual data storage locations have not been formally audited.', score: 2 },
        { text: 'Core SCADA and billing data is within the required jurisdiction; some analytics may use overseas cloud.', score: 3 },
        { text: 'All critical and consumer data stored within compliant national infrastructure; audited annually.', score: 4 },
        { text: 'Zero data egress enforced technically — all operational and consumer data stored within applicable jurisdictional boundaries.', score: 5 }
      ]
    }
  ],

  // ── MANUFACTURING & AUTOMOTIVE ────────────────────────────────────────────
  // Standards are largely international (ISO 9001, FDA 21 CFR, REACH) — single variant

  manufacturing: [
    {
      id: 'comp1',
      text: 'How does your organisation maintain audit-ready production and quality records for ISO 9001 / IATF 16949 certification, FDA 21 CFR Part 11 compliance, or applicable product regulatory requirements?',
      hint: 'Manufacturing organisations face audit requirements from quality certifications, product regulators (FDA, EU CE, BIS), and customer contracts — all requiring demonstrable record integrity.',
      options: [
        { text: 'We are not fully clear on what log and record evidence each standard requires.', score: 1 },
        { text: 'We have retention policies on paper; evidence collection before audits is largely manual.', score: 2 },
        { text: 'We meet minimum retention requirements but pulling production and quality evidence takes significant effort.', score: 3 },
        { text: 'Compliant retention with access-controlled audit trails; evidence packages prepared within a day.', score: 4 },
        { text: 'Automated retention controls, immutable storage, and on-demand evidence generation for all certification and regulatory scopes.', score: 5 }
      ]
    },
    {
      id: 'comp2',
      text: 'Are your production records, quality test results, and ERP/MES transaction logs stored in a tamper-proof manner for regulatory and customer audit?',
      hint: 'FDA 21 CFR Part 11, ISO 9001 and IATF 16949 audit requirements, and automotive traceability standards require that production and quality records cannot be altered retroactively.',
      options: [
        { text: 'Production and quality records are on standard storage and can be modified.', score: 1 },
        { text: 'Some records archived in read-only mode but not formally tamper-evident.', score: 2 },
        { text: 'Quality and inspection records on immutable storage; ERP and operational logs are not.', score: 3 },
        { text: 'Most production, quality, and audit-relevant records on immutable storage with access trails.', score: 4 },
        { text: 'All regulated production records on certified immutable storage with cryptographic integrity verification.', score: 5 }
      ]
    },
    {
      id: 'comp3',
      text: 'How quickly could you respond to an FDA inspection, ISO/IATF surveillance audit, OEM customer quality audit, or product recall investigation requiring production and quality records?',
      hint: 'FDA inspections and customer quality audits can require production records at short notice — often 24 to 72 hours; product recalls may require full batch traceability within hours.',
      options: [
        { text: 'Weeks — production and quality records are distributed and difficult to correlate.', score: 1 },
        { text: 'Several days — possible but requires significant manual effort across quality and IT teams.', score: 2 },
        { text: '24–48 hours with IT and quality team involvement and manual extraction.', score: 3 },
        { text: 'Within 24 hours — search tools can extract and package records for the auditor or authority.', score: 4 },
        { text: 'Within hours — automated evidence package generation with full production batch chain of custody.', score: 5 }
      ]
    },
    {
      id: 'comp4',
      text: 'Do you have role-based access controls on production records, quality data, ERP transactions, and supplier logs?',
      hint: 'Quality management standards and data protection law require that production and customer data in manufacturing systems is accessible only to authorised personnel with a full access audit trail.',
      options: [
        { text: 'No — production system access is not formally controlled or audited.', score: 1 },
        { text: 'Basic team-level access; for example only quality team can access QMS records.', score: 2 },
        { text: 'RBAC defined on QMS and ERP platforms but access auditing is limited.', score: 3 },
        { text: 'Fine-grained RBAC with a full audit trail of all production, quality, and supplier data access.', score: 4 },
        { text: 'Zero-trust access with MFA, just-in-time provisioning, and automated alerts for sensitive production data access.', score: 5 }
      ]
    },
    {
      id: 'comp5',
      text: 'Is your production data, quality records, and customer/supplier data storage compliant with applicable data residency requirements, industry data governance standards, and ESG reporting mandates?',
      hint: 'Some regulatory regimes (FDA, EU product regulations, automotive OEM contracts) specify where production records and quality data must be stored, and for how long. ESG reporting increasingly requires traceable emissions and supply chain data.',
      options: [
        { text: 'No formal data residency or retention policy for production and quality records.', score: 1 },
        { text: 'Policy exists on paper; actual data storage and retention has not been formally audited.', score: 2 },
        { text: 'Core quality and compliance records retained per certification requirements; full data governance is incomplete.', score: 3 },
        { text: 'All regulated production and quality data stored in compliant infrastructure; retention audited annually.', score: 4 },
        { text: 'Full data lifecycle governance — production records, quality data, and supply chain data retained, protected, and accessible for audit, recall, and ESG reporting.', score: 5 }
      ]
    }
  ]

};


// ─── DOMAINS 2–4: Generic (all sectors, all countries) ────────────────────────

var appQuestions = [
  {
    id: 'app1',
    text: 'What is your current APM coverage across production workloads?',
    hint: 'Include internal applications, third-party integrations, and APIs.',
    options: [
      { text: 'No APM — we rely on application logs and user reports.', score: 1 },
      { text: 'APM covers a few critical applications; most workloads are unmonitored.', score: 2 },
      { text: 'APM deployed across most critical applications with basic dashboards.', score: 3 },
      { text: 'Full APM with distributed tracing, code-level diagnostics, and SLO tracking.', score: 4 },
      { text: 'APM fully integrated with business observability; every service has SLOs tied to business SLAs.', score: 5 }
    ]
  },
  {
    id: 'app2',
    text: 'How do you handle third-party API or integration failures that your services depend on?',
    hint: 'Do you know when a dependency is degraded before it causes a failure in your own service?',
    options: [
      { text: 'We find out when the integration fails — no proactive monitoring.', score: 1 },
      { text: 'We monitor endpoint availability but not response quality or payload anomalies.', score: 2 },
      { text: 'We monitor latency and error rates for key third-party dependencies.', score: 3 },
      { text: 'Full dependency mapping with automated alerting on degradation.', score: 4 },
      { text: 'Third-party dependencies are part of end-to-end observability with business-impact scoring.', score: 5 }
    ]
  },
  {
    id: 'app3',
    text: 'Can you trace a slow or failed user request across all services, databases, and external calls?',
    hint: 'Distributed tracing — following one request across a microservices or multi-tier architecture.',
    options: [
      { text: 'No — we examine each service independently.', score: 1 },
      { text: 'We correlate logs across some services using request IDs.', score: 2 },
      { text: 'Distributed tracing exists for major services; gaps remain in databases and external calls.', score: 3 },
      { text: 'Full distributed tracing across services, databases, and external APIs.', score: 4 },
      { text: 'Full tracing linked to business transaction outcomes and user session context.', score: 5 }
    ]
  },
  {
    id: 'app4',
    text: 'Do you have defined and enforced Service Level Objectives (SLOs) for critical applications?',
    hint: 'SLOs are internal targets more granular than the SLAs you commit to customers or regulators.',
    options: [
      { text: 'No SLOs — we have informal uptime expectations only.', score: 1 },
      { text: 'External SLAs exist but internal SLOs are not formally defined.', score: 2 },
      { text: 'SLOs are defined for critical applications and tracked manually.', score: 3 },
      { text: 'SLOs are automated; alerting fires on error-budget burn with team accountability.', score: 4 },
      { text: 'SLOs are integrated with business impact — error-budget depletion triggers business escalation.', score: 5 }
    ]
  },
  {
    id: 'app5',
    text: 'How do you monitor customer-facing digital channels such as mobile apps, web portals, and APIs?',
    hint: 'Real-user monitoring, crash analytics, and API gateway observability.',
    options: [
      { text: 'We rely on app store reviews and customer support calls.', score: 1 },
      { text: 'Basic crash reporting from a mobile SDK; no web or API-layer observability.', score: 2 },
      { text: 'Real-user monitoring and crash analytics on mobile; API gateway logs monitored separately.', score: 3 },
      { text: 'Unified channel observability — mobile, web, and APIs on correlated dashboards.', score: 4 },
      { text: 'Full channel observability linked to transaction success rates and customer experience scores.', score: 5 }
    ]
  }
];

var infraQuestions = [
  {
    id: 'infra1',
    text: 'How complete is your infrastructure inventory and monitoring coverage?',
    hint: 'Include on-premise servers, VMs, containers, network devices, and cloud workloads.',
    options: [
      { text: 'No centralised inventory — each team tracks their own assets.', score: 1 },
      { text: 'Spreadsheet-based inventory; monitoring is fragmented across teams.', score: 2 },
      { text: 'CMDB exists; monitoring covers most compute but network and storage have gaps.', score: 3 },
      { text: 'Comprehensive monitoring across compute, storage, and network with auto-discovery.', score: 4 },
      { text: 'Fully automated infrastructure discovery with real-time topology maps and dependency graphs.', score: 5 }
    ]
  },
  {
    id: 'infra2',
    text: 'Can you monitor network path performance such as latency, jitter, and packet loss between critical application tiers?',
    hint: 'This requires active probing or SNMP/IP SLA polling — distinct from log analysis.',
    options: [
      { text: 'No network performance monitoring beyond ping checks.', score: 1 },
      { text: 'SNMP polling on key switches and routers; no path-level visibility.', score: 2 },
      { text: 'Network monitoring exists but is siloed from application observability.', score: 3 },
      { text: 'Network path analytics — jitter, packet loss, latency — correlated with application performance.', score: 4 },
      { text: 'Full network observability integrated with transaction tracing — network issues linked to business impact.', score: 5 }
    ]
  },
  {
    id: 'infra3',
    text: 'How is infrastructure capacity planning managed?',
    hint: 'Reactive (fix after a breach) or predictive (forecast and pre-provision)?',
    options: [
      { text: 'Reactive — we add capacity after incidents or user complaints.', score: 1 },
      { text: 'Manual quarterly reviews using historical reports.', score: 2 },
      { text: 'Trend-based forecasting using historical metrics for key servers.', score: 3 },
      { text: 'Automated capacity forecasting with proactive provisioning alerts.', score: 4 },
      { text: 'ML-driven capacity intelligence linked to business growth forecasts.', score: 5 }
    ]
  },
  {
    id: 'infra4',
    text: 'How do you handle observability for virtualised and containerised workloads?',
    hint: 'VMware, KVM, Docker, Kubernetes, or OpenShift environments.',
    options: [
      { text: 'No special monitoring — VMs and containers are treated like bare-metal.', score: 1 },
      { text: 'Basic VM host metrics collected; the container layer is not monitored.', score: 2 },
      { text: 'VM-level metrics monitored; some container monitoring exists but not in production.', score: 3 },
      { text: 'Full container observability including pod-level metrics, resource limits, and event tracking.', score: 4 },
      { text: 'Container, host, and network observability unified with workload context and auto-scaling telemetry.', score: 5 }
    ]
  },
  {
    id: 'infra5',
    text: 'Are your primary and DR data centres covered with unified infrastructure observability?',
    hint: 'Including hardware health, power, and cooling — important for regulated on-premise environments.',
    options: [
      { text: 'Physical data centre monitoring is handled by facilities with no IT integration.', score: 1 },
      { text: 'Hardware health alerts exist but are not integrated with IT monitoring.', score: 2 },
      { text: 'Data centre health metrics feed a DCIM or NOC tool but are not correlated with application metrics.', score: 3 },
      { text: 'Data centre health, IT infrastructure, and application performance correlated in a unified NOC view.', score: 4 },
      { text: 'Full DC-to-application observability with predictive alerts linked to risk posture.', score: 5 }
    ]
  }
];

var logQuestions = [
  {
    id: 'log1',
    text: 'How centralised is your log collection across applications, infrastructure, and network devices?',
    hint: 'Server logs, application logs, network syslog, security events, and database audit logs.',
    options: [
      { text: 'Logs sit on individual servers; we SSH in to investigate.', score: 1 },
      { text: 'Partial centralisation — some critical application logs are aggregated but coverage is under 50%.', score: 2 },
      { text: 'Most critical systems send logs centrally; network and database logs have gaps.', score: 3 },
      { text: 'Comprehensive log centralisation with structured parsing and tagging across all tiers.', score: 4 },
      { text: 'Full log data lake — all systems, all tiers, with real-time streaming and fast query.', score: 5 }
    ]
  },
  {
    id: 'log2',
    text: 'What is your current log retention period and query capability?',
    hint: 'Regulators often mandate specific retention periods; query speed matters for incident investigation.',
    options: [
      { text: 'Logs purged frequently (under 30 days) due to storage constraints.', score: 1 },
      { text: '30–90 day hot retention; older logs archived but rarely queried.', score: 2 },
      { text: '90–180 day hot retention; querying older data takes hours.', score: 3 },
      { text: '1-year hot retention, searchable archive, sub-minute query across the full period.', score: 4 },
      { text: 'Tiered storage (hot/warm/cold) with regulatory-aligned retention and real-time query across all tiers.', score: 5 }
    ]
  },
  {
    id: 'log3',
    text: 'Can teams search and correlate logs across different systems in a single query interface?',
    hint: 'For example, correlating an application error with the associated network event and database query.',
    options: [
      { text: 'No — each team uses their own tool or raw log files.', score: 1 },
      { text: 'A shared log viewer exists but search is basic (grep-level).', score: 2 },
      { text: 'A log platform exists with keyword search; cross-system correlation is manual.', score: 3 },
      { text: 'Structured log analytics with cross-source correlation and saved queries.', score: 4 },
      { text: 'ML anomaly detection, automated pattern clustering, and natural-language log query.', score: 5 }
    ]
  },
  {
    id: 'log4',
    text: 'How do you manage log volume and storage cost as your data grows?',
    hint: 'Log data typically grows 30–50% year-on-year.',
    options: [
      { text: 'We delete logs to manage cost; no structured retention policy.', score: 1 },
      { text: 'We manually filter out low-value logs; cost is a growing concern.', score: 2 },
      { text: 'Log sampling and tiered storage are in place; some cost optimisation exists.', score: 3 },
      { text: 'Intelligent log routing — high-value logs go to hot storage, the rest to cold tier automatically.', score: 4 },
      { text: 'Fully managed log lifecycle with ML-driven tiering, deduplication, and per-source cost attribution.', score: 5 }
    ]
  },
  {
    id: 'log5',
    text: 'Can you detect security or operational anomalies from log data in near real-time?',
    hint: 'For example, unusual admin access, privilege escalation, or a sudden spike in error volume.',
    options: [
      { text: 'No automated detection — we review logs reactively after incidents.', score: 1 },
      { text: 'Threshold-based alerts on a few log patterns such as error rate spikes.', score: 2 },
      { text: 'Rules-based detection on security events; limited coverage of operational anomalies.', score: 3 },
      { text: 'Automated anomaly detection across security and operational log streams.', score: 4 },
      { text: 'ML-powered log intelligence — behavioural baselines, multi-source correlation, SOAR integration.', score: 5 }
    ]
  }
];


// ─── SECTOR → BASE ARCHETYPE MAPPING ─────────────────────────────────────────

var sectorArchetypeMap = {
  'Private Sector Bank':                  'bfsi_regulated',
  'Public Sector Bank':                   'bfsi_regulated',
  'NBFC / Fintech':                       'bfsi_regulated',
  'Insurance':                            'bfsi_regulated',
  'Capital Markets / Exchange':           'bfsi_regulated',
  'Payments & Financial Infrastructure':  'payments',
  'IT / Technology':                      'technology',
  'Government / PSU':                     'government',
  'Retail & E-commerce':                  'retail',
  'Telecom':                              'telecom',
  'Energy & Utilities':                   'energy',
  'Manufacturing & Automotive':           'manufacturing',
  'Other Enterprise':                     'technology'
};


// ─── COUNTRY → QUESTION VARIANT RESOLUTION ───────────────────────────────────
// India (default): base archetype (India-specific regulatory content).
// Middle East: _gcc for BFSI; _intl for others.
// All other international: _intl variant where available.
// technology + manufacturing: universal — no country variant.

function resolveArchetype(sector, country) {
  var base = sectorArchetypeMap[sector] || 'technology';
  if (base === 'technology' || base === 'manufacturing') return base;
  if (!country || country === 'India') return base;

  // GCC variant exists for BFSI only — "Middle East" covers UAE, Saudi Arabia, and wider GCC/MENA
  if (base === 'bfsi_regulated' && country === 'Middle East') {
    var gccKey = base + '_gcc';
    if (txnVariants[gccKey] && compVariants[gccKey]) return gccKey;
  }

  // International variant
  var intlKey = base + '_intl';
  if (txnVariants[intlKey] && compVariants[intlKey]) return intlKey;

  return base; // safe fallback — serve India content if no intl variant exists
}


// ─── ASSEMBLY FUNCTION ────────────────────────────────────────────────────────

function getSections(archetype) {
  var arch = (txnVariants[archetype] && compVariants[archetype]) ? archetype : 'technology';
  return [
    {
      id: 'txn', label: 'Business & Transaction Observability', icon: '&#x1F4B3;', color: 'txn',
      hint: 'End-to-end transaction tracing and linkage of IT performance to business outcomes.',
      weight: 30, questions: txnVariants[arch]
    },
    {
      id: 'app', label: 'Application Performance Observability', icon: '&#x26A1;', color: 'app',
      hint: 'Visibility into application behaviour, code-level diagnostics, and service reliability.',
      weight: 20, questions: appQuestions
    },
    {
      id: 'infra', label: 'Infrastructure & Network Observability', icon: '&#x1F5A5;', color: 'infra',
      hint: 'Visibility across servers, networks, storage, cloud, and virtualisation layers.',
      weight: 20, questions: infraQuestions
    },
    {
      id: 'log', label: 'Log Management & Data Lake', icon: '&#x1F4E6;', color: 'log',
      hint: 'Ability to collect, store, query, and act on logs across all IT systems at scale.',
      weight: 15, questions: logQuestions
    },
    {
      id: 'comp', label: 'Compliance & Audit Readiness', icon: '&#x1F6E1;', color: 'comp',
      hint: 'How well your observability stack supports regulatory obligations and internal audit.',
      weight: 15, questions: compVariants[arch]
    }
  ];
}
