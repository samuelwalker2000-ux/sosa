#!/usr/bin/env python3
"""
send_market_report.py
Converts the latest market report from Markdown to styled HTML and sends via SMTP.

Dependencies:
    pip install python-dotenv markdown

Environment variables (set in scripts/.env):
    EMAIL_FROM      Sender address (e.g. samuelwalker2000@gmail.com)
    EMAIL_TO        Recipient address
    SMTP_HOST       e.g. smtp.gmail.com
    SMTP_PORT       587 (TLS) or 465 (SSL)
    SMTP_USER       SMTP login (usually same as EMAIL_FROM)
    SMTP_PASSWORD   Gmail App Password (16 chars, no spaces)
"""

import os
import smtplib
import glob
import sys
import re
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded credentials from {env_path}")
    else:
        print("No .env file found — using system environment variables")
except ImportError:
    print("python-dotenv not installed — using system environment variables")

# Markdown → HTML converter
try:
    import markdown as md_lib
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False
    print("Warning: 'markdown' library not installed. Sending plain text only.")
    print("Fix: pip install markdown")


EMAIL_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #f4f4f7;
    margin: 0;
    padding: 0;
}
.wrapper {
    max-width: 800px;
    margin: 0 auto;
    background-color: #ffffff;
}
.header {
    background-color: #0f172a;
    padding: 28px 32px;
    border-bottom: 3px solid #3b82f6;
}
.header h1 {
    color: #ffffff;
    margin: 0 0 6px 0;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.header .subtitle {
    color: #94a3b8;
    font-size: 13px;
    margin: 0;
}
.hero-bar {
    background-color: #1e293b;
    padding: 14px 32px;
    display: flex;
    gap: 32px;
}
.hero-bar .metric {
    color: #e2e8f0;
    font-size: 13px;
}
.hero-bar .metric span {
    color: #f8fafc;
    font-weight: 700;
    font-size: 15px;
}
.body {
    padding: 28px 32px;
}
h2, h3 {
    color: #0f172a;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 32px;
    margin-bottom: 12px;
    font-size: 15px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
h1 { display: none; }
p { color: #374151; line-height: 1.7; font-size: 14px; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 20px 0;
    font-size: 13px;
}
th {
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 9px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
td {
    padding: 8px 12px;
    border-bottom: 1px solid #f1f5f9;
    color: #374151;
    vertical-align: top;
}
tr:nth-child(even) td { background-color: #f8fafc; }
tr:hover td { background-color: #eff6ff; }
strong { color: #0f172a; }
em { color: #64748b; }
blockquote {
    border-left: 3px solid #3b82f6;
    margin: 16px 0;
    padding: 10px 16px;
    background: #f0f9ff;
    color: #0369a1;
    font-style: normal;
    font-size: 13px;
}
.footer {
    background-color: #f8fafc;
    padding: 18px 32px;
    border-top: 1px solid #e2e8f0;
    color: #94a3b8;
    font-size: 12px;
    text-align: center;
}
ul, ol { color: #374151; font-size: 14px; line-height: 1.7; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 24px 0; }
code {
    background: #f1f5f9;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 12px;
    color: #0f172a;
}
"""


def color_pct(html: str) -> str:
    """Color-code percentage changes in table cells: green for gains, red for losses."""
    def replace(m):
        val = m.group(0)
        num_str = val.replace('%', '').replace('+', '').strip()
        try:
            num = float(num_str)
            if num > 0:
                return f'<td style="color:#16a34a;font-weight:600">{val}</td>'
            elif num < 0:
                return f'<td style="color:#dc2626;font-weight:600">{val}</td>'
        except ValueError:
            pass
        return f'<td>{val}</td>'

    return re.sub(r'<td>[+\-]?\d+\.?\d*%</td>', replace, html)


def md_to_html(text: str, date_str: str) -> str:
    """Convert Markdown report to a complete styled HTML email."""

    # Extract header metrics from the first bold line
    btc_price = fear_greed = btc_dom = "—"
    for line in text.splitlines():
        if line.startswith("**BTC:") or line.startswith("**BTC :"):
            parts = [p.strip().strip("*") for p in line.split("|")]
            if len(parts) >= 3:
                btc_price  = parts[0].replace("BTC:", "").replace("BTC :", "").strip()
                fear_greed = parts[1].replace("Fear & Greed:", "").strip()
                btc_dom    = parts[2].replace("BTC Dominance:", "").strip()
            break

    raw_html = md_lib.markdown(
        text,
        extensions=["tables", "nl2br"],
        extension_configs={"nl2br": {}}
    )
    raw_html = color_pct(raw_html)

    # Build inline-styled version (Gmail strips <style> blocks)
    inline_css = EMAIL_CSS.replace("\n", " ")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Market Report — {date_str}</title>
  <style>{inline_css}</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <h1 class="title">DAILY MARKET REPORT</h1>
    <p class="subtitle">{date_str} &nbsp;·&nbsp; Powered by Claude + Live Web Data</p>
  </div>

  <table class="hero-bar" style="width:100%;background:#1e293b;padding:14px 32px;border-collapse:collapse;">
    <tr>
      <td style="padding:8px 24px 8px 0;color:#94a3b8;font-size:13px;font-family:sans-serif;">
        BTC &nbsp;<strong style="color:#f8fafc;font-size:16px;">{btc_price}</strong>
      </td>
      <td style="padding:8px 24px;color:#94a3b8;font-size:13px;font-family:sans-serif;">
        Fear &amp; Greed &nbsp;<strong style="color:#f8fafc;font-size:16px;">{fear_greed}</strong>
      </td>
      <td style="padding:8px 0 8px 24px;color:#94a3b8;font-size:13px;font-family:sans-serif;">
        BTC Dominance &nbsp;<strong style="color:#f8fafc;font-size:16px;">{btc_dom}</strong>
      </td>
    </tr>
  </table>

  <div class="body">
    {raw_html}
  </div>

  <div class="footer">
    Generated daily at 7:00 AM ET &nbsp;·&nbsp; For informational purposes only. Not financial advice.
    <br>samuelwalker2000@gmail.com
  </div>

</div>
</body>
</html>"""

    return html


def get_latest_report():
    workspace_root = Path(__file__).parent.parent
    reports_dir = workspace_root / "outputs" / "market-reports"
    if not reports_dir.exists():
        raise FileNotFoundError(f"Reports directory not found: {reports_dir}")
    reports = sorted(glob.glob(str(reports_dir / "*.md")), reverse=True)
    if not reports:
        raise FileNotFoundError(
            f"No report files in {reports_dir}. Run /market-report first."
        )
    return Path(reports[0])


def send_report():
    required = ["EMAIL_FROM", "EMAIL_TO", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}")
        print("Set these in scripts/.env — see scripts/.env.example")
        sys.exit(1)

    email_from    = os.environ["EMAIL_FROM"]
    email_to      = os.environ["EMAIL_TO"]
    smtp_host     = os.environ["SMTP_HOST"]
    smtp_port     = int(os.environ.get("SMTP_PORT", 587))
    smtp_user     = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]

    report_path    = get_latest_report()
    report_md      = report_path.read_text(encoding="utf-8")
    date_str       = datetime.today().strftime("%B %d, %Y")
    date_file_str  = datetime.today().strftime("%Y-%m-%d")
    subject        = f"Daily Market Report — {date_file_str}"

    print(f"Report:  {report_path.name}")
    print(f"Sending: {email_to}")
    print(f"Subject: {subject}")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = email_from
    msg["To"]      = email_to

    # Plain text fallback
    msg.attach(MIMEText(report_md, "plain", "utf-8"))

    # HTML part (preferred by email clients)
    if HAS_MARKDOWN:
        html_body = md_to_html(report_md, date_str)
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        print("Format:  HTML (with plain-text fallback)")
    else:
        print("Format:  Plain text only (install 'markdown' for HTML)")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, [email_to], msg.as_string())
        print(f"SUCCESS: Report sent to {email_to}")
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Authentication failed. Use a Gmail App Password, not your regular password.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    send_report()
