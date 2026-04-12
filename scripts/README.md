# Scripts

This directory contains automation scripts for the Claude workspace.

---

## send_market_report.py

Sends the most recent daily market report from `outputs/market-reports/` to your email inbox via SMTP.

### First-time setup

**Step 1 — Create your `.env` file**

```bash
cp scripts/.env.example scripts/.env
```

Open `scripts/.env` and fill in `SMTP_PASSWORD` with a Gmail App Password (see below). The other fields are already pre-filled for samuelwalker2000@gmail.com.

**Step 2 — Generate a Gmail App Password**

1. Go to [myaccount.google.com](https://myaccount.google.com) and sign in
2. Navigate to **Security** > **2-Step Verification** (enable it if not already on)
3. Go to **Security** > **App Passwords**
4. Select app: **Mail** — Select device: **Windows Computer**
5. Click **Generate** — copy the 16-character password shown
6. Paste it as `SMTP_PASSWORD` in `scripts/.env`

> Your real Gmail password will NOT work here. You must use an App Password.

**Step 3 — Install python-dotenv (optional but recommended)**

```bash
pip install python-dotenv
```

Without this, the script falls back to reading system environment variables. With it, the script reads from `scripts/.env` automatically.

### Running manually

```bash
python scripts/send_market_report.py
```

The script will:
1. Find the most recent `.md` file in `outputs/market-reports/`
2. Send it to samuelwalker2000@gmail.com with subject `Daily Market Report — YYYY-MM-DD`
3. Print success or a clear error message

### Automated daily delivery

The daily report is generated and emailed automatically each morning at **7:00 AM Eastern** via a Claude Code scheduled remote agent. The agent:

1. Runs `/market-report` to generate the report with live web data
2. Saves it to `outputs/market-reports/`
3. Uploads it to Google Drive (folder: "Market Reports")
4. Calls this script to send the email

To check or manage the schedule, run `/schedule` in Claude Code.

### Troubleshooting

| Error | Fix |
|---|---|
| `Authentication failed` | Use an App Password, not your regular Gmail password |
| `Missing environment variables` | Check that `scripts/.env` exists and is filled in |
| `No market report files found` | Run `/market-report` first to generate a report |
| `SMTPException` | Check that SMTP_HOST=smtp.gmail.com and SMTP_PORT=587 |
