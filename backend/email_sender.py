import os
import base64

ENV = os.getenv('ENV', 'development')


def send_report_email(data):
    if ENV == 'development':
        _console_email(data)
    else:
        _gmail_api_email(data)


def _console_email(data):
    scores = data.get('scores', {})
    overall = scores.get('overall', '—')
    band = data.get('maturity_band', '—')
    name = f"{data.get('first_name','')} {data.get('last_name','')}".strip() or 'Respondent'

    domain_rows = ''
    for key, label in [('txn','Business & Transaction'), ('app','Application Performance'),
                       ('infra','Infrastructure & Network'), ('log','Log Management'),
                       ('comp','Compliance & Audit')]:
        pct = scores.get(key, {}).get('pct', '—')
        domain_rows += f"  {label:<30} {pct}%\n"

    print('\n' + '=' * 65)
    country = data.get('country', '')
    print(f'TO:      {data.get("email")}')
    print(f'SUBJECT: Your Observability Maturity Report — {overall}/100 ({band})')
    print('-' * 65)
    print(f'Hi {name},')
    if country:
        print(f'Country: {country}')
    print()
    print(f'Your overall maturity score: {overall}/100 — {band}\n')
    print('Domain breakdown:')
    print(domain_rows)
    print('Contact info@vunetsystems.com to discuss your results.')
    print('=' * 65 + '\n')


def _gmail_api_email(data):
    import json
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    creds_b64 = os.getenv('GMAIL_SA_CREDENTIALS_JSON', '')
    if not creds_b64:
        raise RuntimeError('GMAIL_SA_CREDENTIALS_JSON not set')

    creds_json = json.loads(base64.b64decode(creds_b64).decode())
    sender = os.getenv('GMAIL_SENDER', 'info@vunetsystems.com')

    credentials = service_account.Credentials.from_service_account_info(
        creds_json,
        scopes=['https://www.googleapis.com/auth/gmail.send'],
        subject=sender,
    )
    service = build('gmail', 'v1', credentials=credentials)

    msg = _build_html_email(data, sender)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()


def _build_html_email(data, sender):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    scores  = data.get('scores', {})
    overall = scores.get('overall', 0)
    band    = data.get('maturity_band', '')
    name    = f"{data.get('first_name','')} {data.get('last_name','')}".strip() or 'there'
    to_addr = data.get('email', '')

    domain_rows_html = ''
    for key, label in [('txn','Business & Transaction'), ('app','Application Performance'),
                       ('infra','Infrastructure & Network'), ('log','Log Management'),
                       ('comp','Compliance & Audit')]:
        pct = scores.get(key, {}).get('pct', 0)
        domain_rows_html += f'<tr><td style="padding:6px 12px;border-bottom:1px solid #eee;">{label}</td><td style="padding:6px 12px;border-bottom:1px solid #eee;font-weight:600;">{pct}%</td></tr>'

    html = f"""
<!DOCTYPE html><html><body style="font-family:sans-serif;color:#0f1923;background:#f9fafb;padding:0;margin:0;">
<div style="max-width:560px;margin:32px auto;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e5e7eb;">
  <div style="background:#0f1923;padding:28px 32px;">
    <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:0 0 8px;">Observability Maturity Index</p>
    <h1 style="color:#fff;font-size:22px;margin:0 0 4px;">Your Assessment Report</h1>
    <p style="color:rgba(255,255,255,0.55);font-size:13px;margin:0;">Hi {name}, here are your results.</p>
  </div>
  <div style="padding:28px 32px;">
    <div style="background:#f9fafb;border-radius:8px;padding:20px;text-align:center;margin-bottom:24px;">
      <div style="font-size:48px;font-weight:700;color:#0f1923;line-height:1;">{overall}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">out of 100</div>
      <div style="display:inline-block;background:#fdf0f7;color:#9c0560;font-size:12px;font-weight:600;padding:4px 14px;border-radius:20px;margin-top:10px;">{band}</div>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <thead><tr style="background:#f3f4f6;"><th style="padding:8px 12px;text-align:left;">Domain</th><th style="padding:8px 12px;text-align:left;">Score</th></tr></thead>
      <tbody>{domain_rows_html}</tbody>
    </table>
    <p style="font-size:13px;color:#374151;margin:24px 0 8px;">Want to discuss your results and improvement roadmap?</p>
    <a href="mailto:info@vunetsystems.com" style="display:inline-block;background:#C60675;color:#fff;text-decoration:none;padding:10px 22px;border-radius:8px;font-size:13px;font-weight:600;">Contact VuNet Systems</a>
  </div>
  <div style="padding:16px 32px;border-top:1px solid #e5e7eb;font-size:11px;color:#9ca3af;">
    Observability Maturity Index &mdash; An industry benchmark initiative by VuNet Systems.
  </div>
</div>
</body></html>
"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Your Observability Maturity Report — {overall}/100 ({band})'
    msg['From']    = sender
    msg['To']      = to_addr
    msg.attach(MIMEText(html, 'html'))
    return msg
