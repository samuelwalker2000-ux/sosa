# Plan: Email Formatting Upgrade — HTML + Visual Polish

**Created:** 2026-04-12
**Status:** Draft
**Request:** Upgrade the daily market report email from plain text to a visually formatted HTML email, with tables rendering properly, bold text working, and a clean newsletter-style layout.

---

## Overview

### What This Plan Accomplishes

Rewrites `scripts/send_market_report.py` to convert the Markdown report to styled HTML before sending. The email will render properly in Gmail and other clients: tables as real tables, headers styled, bold text working, sections visually separated. Also upgrades the plain-text fallback so the email is readable even if HTML rendering is disabled.

### Why This Matters

The daily report currently arrives as raw Markdown — tables are unreadable pipes, bold asterisks are visible, and the structure is hard to skim quickly at 7 AM. A properly formatted HTML email makes the report actually usable as a morning briefing at a glance.

---

## Current State

### Relevant Existing Structure

```
scripts/
├── send_market_report.py    # Current script — sends plain text only
├── .env                     # Gmail credentials (gitignored)
├── .env.example             # Credential template
└── README.md                # Setup instructions

outputs/market-reports/
└── 2026-04-12-market-report.md   # First live report — template for formatting
```

### Gaps or Problems Being Addressed

- Email body is raw Markdown — `**bold**`, `| table |` pipes, `###` headers all visible as literal characters
- Tables are completely unreadable in email clients
- No visual hierarchy — 12 sections blur together
- Hard to skim quickly; defeats the purpose of a morning brief

---

## Proposed Changes

### Summary of Changes

- Add `markdown` Python library to convert report Markdown → HTML
- Add CSS styling inline (required for Gmail compatibility — Gmail strips `<style>` tags)
- Rewrite `send_market_report.py` to send `multipart/alternative` with both HTML and plain-text parts
- Style the HTML: dark header bar, section dividers, readable table formatting, color-coded sentiment (green/red for gainers/losers)
- Keep plain-text fallback clean with simple ASCII formatting
- Update `scripts/README.md` with new dependency (`pip install markdown`)
- Commit updated script to GitHub so the daily scheduled trigger picks it up automatically

### New Files to Create

None — modifying existing script only.

### Files to Modify

| File Path | Changes |
|---|---|
| `scripts/send_market_report.py` | Full rewrite: Markdown→HTML conversion, inline CSS, multipart email |
| `scripts/README.md` | Add `markdown` to dependencies section |
| `scripts/.env.example` | No changes needed |

---

## Design Decisions

### Key Decisions Made

1. **Inline CSS only**: Gmail strips `<style>` blocks and `<head>` content. All styling must be `style="..."` attributes on individual elements. This is more verbose but the only approach that works reliably across Gmail, Outlook, and Apple Mail.

2. **`markdown` library over `mistune` or `commonmark`**: The `markdown` Python library is the most widely used, stable, and produces clean HTML output with table extension support. Install: `pip install markdown`.

3. **Dark header + light body**: Matches the "analyst terminal" aesthetic of the report content. Header bar in dark charcoal (#1a1a2e), body in white, section headers in a muted navy, tables with alternating row shading.

4. **Color coding for gainers/losers**: Green (#16a34a) for positive % changes, red (#dc2626) for negative. Applied to the 24h % column in the gainers/losers tables.

5. **Multipart/alternative email**: Sends both HTML and plain-text versions. Email clients show HTML when supported; plain text as fallback. Current plain-text version stays as the fallback — no changes needed there.

6. **No external images or CDN assets**: Keeps the email self-contained and avoids spam filters. Pure HTML/CSS only.

### Alternatives Considered

- **`mistune`**: Faster but less battle-tested table support. Rejected.
- **SendGrid templating**: Overkill for a single-recipient personal email. Rejected.
- **Attaching the `.md` file**: Cleaner but requires opening an attachment to read. Rejected — the value is reading in the email preview.

### Open Questions

None — proceeding with HTML email with inline CSS.

---

## Step-by-Step Tasks

### Step 1: Install `markdown` library

Install the Python `markdown` library which handles Markdown-to-HTML conversion including table support.

**Actions:**
- Run: `pip install markdown`
- Verify: `python -c "import markdown; print('ok')"`

**Files affected:** None (system library)

---

### Step 2: Rewrite `scripts/send_market_report.py`

Replace the current script with a version that:
1. Reads the `.md` report file
2. Converts it to HTML using the `markdown` library with `tables` extension
3. Wraps the HTML in a styled email template with inline CSS
4. Sends as `multipart/alternative` (HTML + plain text fallback)

**Full new script:**

```python
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
```

**Files affected:**
- `scripts/send_market_report.py`

---

### Step 3: Install `markdown` library

**Actions:**
- Run: `pip install markdown`
- Confirm: `python -c "import markdown; print('ok')"`

---

### Step 4: Test — send a formatted email

**Actions:**
- Run: `python scripts/send_market_report.py`
- Check Gmail — confirm tables render, header bar appears, % changes are colour-coded
- Review on mobile (Gmail app) as well as desktop

---

### Step 5: Update `scripts/README.md`

Add `markdown` to the dependencies section.

**Actions:**
- Add `pip install markdown` under the setup steps alongside `pip install python-dotenv`

---

### Step 6: Commit and push to GitHub

Commit the updated script and README so the daily scheduled trigger picks up the new HTML version automatically.

**Actions:**
- `git add scripts/send_market_report.py scripts/README.md`
- `git commit -m "Upgrade email to HTML with inline CSS and styled tables"`
- `git push`

---

## Validation Checklist

- [ ] `pip install markdown` completes without error
- [ ] `python scripts/send_market_report.py` runs and prints `Format: HTML`
- [ ] Email received in Gmail with visible header bar (dark background, white text)
- [ ] Tables render as real HTML tables (not pipe characters)
- [ ] Positive % values appear green, negative appear red in gainers/losers tables
- [ ] Bold text renders correctly (not `**asterisks**`)
- [ ] Section headers are styled and visually separated
- [ ] Plain text fallback is present (check via Gmail's "Show original")
- [ ] Changes pushed to GitHub (so daily trigger uses new version)

---

## Success Criteria

1. The daily email renders in Gmail as a styled HTML newsletter — not raw Markdown
2. Tables are readable, % changes are colour-coded, sections have visual hierarchy
3. The script remains a single file with no external dependencies beyond `markdown` and `python-dotenv`
4. Changes are live on GitHub so the scheduled remote agent sends HTML automatically

---

## Notes

- **Gmail CSS support:** Gmail strips `<style>` blocks and `<head>` CSS. All styles in the template use `style="..."` inline attributes on the elements that need them, which Gmail does render correctly.
- **Outlook compatibility:** Outlook (desktop) has poor CSS support. Tables will render but some visual polish may be lost. The report is primarily read in Gmail, so Gmail is the rendering target.
- **Future enhancement:** Add a summary section at the top of the email (5-bullet TL;DR above the fold) so the most important points are visible without scrolling. This would be a small addition to the `/market-report` command prompt, not the email script.
