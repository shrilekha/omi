# Observability Maturity Index (OMI)

A self-service web assessment tool for enterprise technology leaders. Respondents complete a 25-question maturity assessment across five observability domains and receive a scored report with gap analysis.

---

## Local setup (under 5 minutes)

**Requirements:** Python 3.9+

```bash
# 1. Clone / navigate to the project root
cd c:\Shrilekha\OMI

# 2. Copy and configure the environment file
copy .env.example .env
# .env already has ENV=development — no changes needed for local use

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Run
python app.py
```

Open **http://localhost:5050** in your browser.

**Testing tips:**
- Use `test@test.com` as the email address to bypass business-email validation
- Emails are printed to the terminal — no real email is sent in development mode
- The SQLite database is auto-created at `local_dev.db` (project root) on first run
- Changing sector at registration shows different questions for domains 1 and 5

---

## Production setup (Ubuntu VM)

**Requirements:** Python 3.9+, MySQL 8+

### 1. Create the database

```sql
CREATE DATABASE omi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'omi_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON omi_db.* TO 'omi_user'@'localhost';
FLUSH PRIVILEGES;
```

Then run the schema:
```bash
mysql -u omi_user -p omi_db < database/schema.sql
```

### 2. Configure the environment

```bash
copy .env.example .env
```

Edit `.env`:
```
ENV=production
DB_HOST=localhost
DB_USER=omi_user
DB_PASS=your-strong-password
DB_NAME=omi_db
SECRET_KEY=generate-a-strong-random-key
```

### 3. Gmail API (for sending report emails)

1. Create a Google Cloud project and enable the Gmail API
2. Create a service account with domain-wide delegation
3. Grant the service account the `https://www.googleapis.com/auth/gmail.send` scope
4. Download the service account JSON key file
5. Base64-encode it:
   ```bash
   base64 -w 0 service_account.json
   ```
6. Paste the result into `.env`:
   ```
   GMAIL_SA_CREDENTIALS_JSON=<base64 string>
   GMAIL_SENDER=omi@vunetsystems.com
   ```

### 4. Run with Gunicorn

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5050 app:app
```

Serve behind Nginx with SSL for production.

---

## Project structure

```
OMI/
├── frontend/
│   ├── index.html          # Full single-page app (all 4 screens)
│   ├── questions.js        # All questions — edit here to update content
│   └── assets/
│       └── style.css       # All styles
├── backend/
│   ├── app.py              # Flask app — routes and startup
│   ├── db.py               # DB abstraction (SQLite in dev, MySQL in prod)
│   ├── email_sender.py     # Email (console in dev, Gmail API in prod)
│   └── requirements.txt
├── database/
│   └── schema.sql          # MySQL schema for production
├── scripts/
│   └── export_questions_to_excel.py  # Dumps all questions/options to OMI_Questions_Review.xlsx
├── OMI_Questions_Review.xlsx  # Generated — for content review, re-run the script above after edits
├── .env.example            # All config variables with comments
└── README.md
```

---

## Editing questions

All scored question content lives in `frontend/questions.js`. No other file needs to change for wording/option edits within an existing question.

- Domains 2–4 (Application Performance, Infrastructure, Log Management) are in `appQuestions`, `infraQuestions`, and `logQuestions` — shared across all sectors and countries.
- Domains 1 and 5 (Business & Transaction Observability, Compliance & Audit Readiness) have sector **and country** variants in `txnVariants` and `compVariants`, because the transactions and regulations in play genuinely differ by market. Each key is a sector archetype: `bfsi_regulated`, `payments`, `government`, `technology`, `retail`, `telecom`, `energy`, `manufacturing`.
- Country variants use the suffix convention `{sector}`, `{sector}_gcc`, `{sector}_intl`:
  - *(no suffix)* — India (default), India-specific regulatory references (RBI/SEBI, NPCI, TRAI, CERC/SERC, …)
  - `_gcc` — UAE / Saudi Arabia / wider GCC — **BFSI only** (CBUAE, SAMA); other sectors fall back to `_intl` in the Gulf
  - `_intl` — Singapore, UK, US, Australia, other international (MAS TRM, FCA, APRA CPS 230, FFIEC, Ofcom/FCC, …)
  - `technology` and `manufacturing` are treated as country-agnostic (their standards are already international) and have no `_intl`/`_gcc` variant
  - `resolveArchetype()` in `questions.js` does the sector+country → archetype resolution; `getSections()` assembles the final 25-question set from it
- The `sectorArchetypeMap` object maps the registration sector dropdown to the right base archetype.
- Each question has exactly 5 **scored** answer options, 1–5 (1 = least mature, 5 = most mature). A 6th "Not sure / not applicable to my role" option is appended to every question by the assessment UI itself (`frontend/index.html`, `renderSection()`) — it's universal, not per-question, so it lives in code rather than in `questions.js`, and is excluded from scoring rather than counted as a low score.
- After editing questions, re-run `python scripts/export_questions_to_excel.py` to refresh `OMI_Questions_Review.xlsx` for content review — it reads directly from `questions.js` so it can drift out of sync if regenerated only some of the time.

---

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the SPA |
| `POST` | `/api/submit` | Receives assessment results, saves to DB, sends email |
| `GET` | `/api/health` | Health check — returns `{"status":"ok","env":"..."}` |

### `/api/submit` payload

```json
{
  "session_id":       "uuid",
  "email":            "user@org.com",
  "first_name":       "Jane",
  "last_name":        "Smith",
  "role":             "CTO / CIO",
  "sector":           "Private Sector Bank",
  "sector_archetype": "bfsi_regulated",
  "question_variant": "bfsi_regulated",
  "domain_tools":     { "txn": "Dynatrace", "app": "Datadog", "infra": "None / no dedicated tool", ... },
  "answers":          { "txn1": 3, "txn2": 2, ... },
  "scores":           { "txn": { "pct": 52 }, ..., "overall": 58 },
  "maturity_band":    "Structured"
}
```

`answers` values are either a score `1`–`5` or the string `"na"` — respondents can mark any question "Not sure / not applicable" if it falls outside their visibility (e.g. an application lead answering infrastructure questions). `"na"` answers are excluded from that domain's scoring denominator rather than counted as a low score; a domain with zero scoreable answers reports `pct: null` ("Not assessed").

---

## Maturity bands

| Score | Band |
|---|---|
| 0–24 | Reactive |
| 25–44 | Aware |
| 45–64 | Structured |
| 65–81 | Proactive |
| 82–100 | Adaptive |

---

## Domain weights

| Domain | Weight |
|---|---|
| Business & Transaction Observability | 30% |
| Application Performance | 20% |
| Infrastructure & Network | 20% |
| Log Management & Data Lake | 15% |
| Compliance & Audit Readiness | 15% |
