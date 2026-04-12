#!/usr/bin/env python3
"""
send_market_report.py
Sends the latest market report from outputs/market-reports/ via SMTP email.

Usage:
    python scripts/send_market_report.py

Environment variables (set in scripts/.env or system environment):
    EMAIL_FROM      Sender email address (e.g. samuelwalker2000@gmail.com)
    EMAIL_TO        Recipient email address
    SMTP_HOST       SMTP server hostname (e.g. smtp.gmail.com)
    SMTP_PORT       SMTP port — 587 for TLS (default), 465 for SSL
    SMTP_USER       SMTP login username (usually same as EMAIL_FROM)
    SMTP_PASSWORD   Gmail App Password (NOT your regular Gmail password)

Gmail setup:
    1. Enable 2-Step Verification on your Google account
    2. Go to myaccount.google.com > Security > App Passwords
    3. Generate an App Password for "Mail" / "Windows Computer"
    4. Use that 16-character password as SMTP_PASSWORD
"""

import os
import smtplib
import glob
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load .env file if present (requires: pip install python-dotenv)
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
    print("To install: pip install python-dotenv")


def get_latest_report():
    """Find the most recent market report .md file."""
    workspace_root = Path(__file__).parent.parent
    reports_dir = workspace_root / "outputs" / "market-reports"

    if not reports_dir.exists():
        raise FileNotFoundError(f"Reports directory does not exist: {reports_dir}")

    reports = sorted(
        glob.glob(str(reports_dir / "*.md")),
        reverse=True
    )

    if not reports:
        raise FileNotFoundError(
            f"No market report files found in {reports_dir}\n"
            "Run /market-report in Claude Code first to generate today's report."
        )

    return Path(reports[0])


def send_report():
    """Load the latest report and send it via SMTP."""

    # --- Load required config ---
    required_vars = ["EMAIL_FROM", "EMAIL_TO", "SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Set these in scripts/.env — see scripts/.env.example for the template.")
        sys.exit(1)

    email_from    = os.environ["EMAIL_FROM"]
    email_to      = os.environ["EMAIL_TO"]
    smtp_host     = os.environ["SMTP_HOST"]
    smtp_port     = int(os.environ.get("SMTP_PORT", 587))
    smtp_user     = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]

    # --- Find report ---
    report_path = get_latest_report()
    report_content = report_path.read_text(encoding="utf-8")
    date_str = datetime.today().strftime("%Y-%m-%d")
    subject = f"Daily Market Report — {date_str}"

    print(f"Report file: {report_path.name}")
    print(f"Sending to:  {email_to}")
    print(f"Subject:     {subject}")

    # --- Build email ---
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = email_from
    msg["To"]      = email_to

    # Plain text part
    msg.attach(MIMEText(report_content, "plain", "utf-8"))

    # --- Send via SMTP with STARTTLS ---
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, [email_to], msg.as_string())

        print(f"SUCCESS: Report sent to {email_to}")

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Authentication failed.")
        print("For Gmail, make sure you're using an App Password, not your regular password.")
        print("See: myaccount.google.com > Security > App Passwords")
        sys.exit(1)

    except smtplib.SMTPException as e:
        print(f"ERROR: SMTP error — {e}")
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Unexpected error — {e}")
        sys.exit(1)


if __name__ == "__main__":
    send_report()
