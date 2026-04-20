# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Is

This is a **Claude Workspace Template** — a structured environment designed for working with Claude Code as a powerful agent assistant across sessions. The user will spin up fresh Claude Code sessions repeatedly, using `/prime` at the start of each to load essential context without bloat.

**This file (CLAUDE.md) is the foundation.** It is automatically loaded at the start of every session. Keep it current — it is the single source of truth for how Claude should understand and operate within this workspace.

---

## The Claude-User Relationship

Claude operates as an **agent assistant** with access to the workspace folders, context files, commands, and outputs. The relationship is:

- **User**: Defines goals, provides context about their role/function, and directs work through commands
- **Claude**: Reads context, understands the user's objectives, executes commands, produces outputs, and maintains workspace consistency

Claude should always orient itself through `/prime` at session start, then act with full awareness of who the user is, what they're trying to achieve, and how this workspace supports that.

---

## Workspace Structure

```
.
├── CLAUDE.md              # This file — core context, always loaded
├── .claude/
│   └── commands/          # Slash commands Claude can execute
│       ├── prime.md           # /prime — session initialization
│       ├── create-plan.md     # /create-plan — create implementation plans
│       ├── implement.md       # /implement — execute plans
│       └── market-report.md   # /market-report — daily crypto/macro report
├── context/               # Background context about the user and project
│                          # (User should populate with role, goals, strategies)
├── plans/                 # Implementation plans created by /create-plan
├── outputs/
│   └── market-reports/    # Daily market report archive (YYYY-MM-DD-market-report.md)
├── reference/             # Templates, examples, reusable patterns
├── scripts/               # Automation scripts
│   ├── send_market_report.py  # Emails latest report via SMTP
│   ├── run_market_report.bat  # Legacy local automation (superseded by Claude Routines)
│   ├── send_log.txt           # Log output from local runs (gitignored)
│   ├── .env                   # Gmail credentials for local use (gitignored)
│   ├── .env.example           # Credential template (copy to .env, never commit)
│   └── README.md              # Setup instructions for email delivery
└── .github/
    └── workflows/
        └── send-market-report.yml  # GitHub Action — emails report on push to main/claude/*
```

**Key directories:**

| Directory    | Purpose                                                                             |
| ------------ | ----------------------------------------------------------------------------------- |
| `context/`   | Who the user is, their role, current priorities, strategies. Read by `/prime`.      |
| `plans/`     | Detailed implementation plans. Created by `/create-plan`, executed by `/implement`. |
| `outputs/`   | Deliverables, analyses, reports, and work products.                                 |
| `reference/` | Helpful docs, templates and patterns to assist in various workflows.                |
| `scripts/`   | Any automation or tooling scripts.                                                  |

---

## Commands

### /prime

**Purpose:** Initialize a new session with full context awareness.

Run this at the start of every session. Claude will:

1. Read CLAUDE.md and context files
2. Summarize understanding of the user, workspace, and goals
3. Confirm readiness to assist

### /create-plan [request]

**Purpose:** Create a detailed implementation plan before making changes.

Use when adding new functionality, commands, scripts, or making structural changes. Produces a thorough plan document in `plans/` that captures context, rationale, and step-by-step tasks.

Example: `/create-plan add a competitor analysis command`

### /implement [plan-path]

**Purpose:** Execute a plan created by /create-plan.

Reads the plan, executes each step in order, validates the work, and updates the plan status.

Example: `/implement plans/2026-01-28-competitor-analysis-command.md`

### /market-report

**Purpose:** Generate today's personalised daily brief covering markets, AI, Arsenal FC, fitness, and MEP engineering.

Uses live web search to fetch all data — no estimates or guesses. Target read time: 2 minutes. Produces an 11-section report covering:
- Macro snapshot (BTC, S&P, NASDAQ, VIX, DXY, Oil, Yields)
- My Take (opinionated positioning stance)
- Crypto (BTC + alts — compact, one section)
- Top movers (top 5 gainers/losers)
- Setups to watch
- Stocks & ETFs (SPY, QQQ, sector rotation, earnings)
- AI news (top 2–3 items)
- Arsenal FC (latest result, next fixture, headlines)
- Fitness (one running or strength training insight)
- MEP Engineering (one technical item — OBC, ASHRAE, NFPA, or HVAC)
- Upcoming catalysts (14-day calendar)

After generating:
1. Saves report to `outputs/market-reports/YYYY-MM-DD-market-report.md`
2. Commits and pushes to GitHub
3. GitHub Action (`.github/workflows/send-market-report.yml`) automatically emails the report to samuelwalker2000@gmail.com

Run manually any time, or triggered automatically each morning at **7:00 AM EDT** by a **Claude Routine** (cloud-hosted, runs whether or not the local machine is on).

**Automation stack:**
- Claude Routine ID: `trig_01FuueawPjM4sPwz9PgfVjKZ` — manage at [claude.ai/code/routines](https://claude.ai/code/routines)
- GitHub Action: triggered on push to `main` or `claude/**` when a file in `outputs/market-reports/` changes
- Gmail credential: stored as GitHub Secret `SMTP_PASSWORD` on the `sosa` repo — no local `.env` required

---

## Scripts

### scripts/send_market_report.py

Reads the most recent file from `outputs/market-reports/`, converts the Markdown to styled HTML, and sends a formatted newsletter-style email to samuelwalker2000@gmail.com via SMTP. Sends as `multipart/alternative` (HTML + plain-text fallback). Requires `pip install python-dotenv markdown`.

Reads credentials from environment variables (or `scripts/.env` as fallback for local use).

**Run manually:**
```bash
EMAIL_FROM=samuelwalker2000@gmail.com \
EMAIL_TO=samuelwalker2000@gmail.com \
SMTP_HOST=smtp.gmail.com SMTP_PORT=587 \
SMTP_USER=samuelwalker2000@gmail.com \
SMTP_PASSWORD=<app-password> \
python scripts/send_market_report.py
```

### .github/workflows/send-market-report.yml

GitHub Action that fires whenever a `.md` file is pushed to `outputs/market-reports/` on `main` or any `claude/**` branch. Installs dependencies and runs `send_market_report.py` using the `SMTP_PASSWORD` GitHub Secret.

**Credential:** stored as repository secret `SMTP_PASSWORD` at `github.com/samuelwalker2000-ux/sosa/settings/secrets/actions`.

### Automation: Claude Routines (cloud)

The daily report runs entirely in Anthropic's cloud — no local machine required.

| Component | Details |
|---|---|
| Routine | `trig_01FuueawPjM4sPwz9PgfVjKZ` at [claude.ai/code/routines](https://claude.ai/code/routines) |
| Schedule | 7:00 AM EDT daily (`0 11 * * *` UTC) |
| Repo | `github.com/samuelwalker2000-ux/sosa` |
| What it does | Generates report, commits and pushes to GitHub |
| Email trigger | GitHub Action fires on push, sends styled HTML email |

**Legacy:** `scripts/run_market_report.bat` and Windows Task Scheduler (`DailyMarketReport`) are superseded and can be disabled.

---

## Critical Instruction: Maintain This File

**Whenever Claude makes changes to the workspace, Claude MUST consider whether CLAUDE.md needs updating.**

After any change — adding commands, scripts, workflows, or modifying structure — ask:

1. Does this change add new functionality users need to know about?
2. Does it modify the workspace structure documented above?
3. Should a new command be listed?
4. Does context/ need new files to capture this?

If yes to any, update the relevant sections. This file must always reflect the current state of the workspace so future sessions have accurate context.

**Examples of changes requiring CLAUDE.md updates:**

- Adding a new slash command → add to Commands section
- Creating a new output type → document in Workspace Structure or create a section
- Adding a script → document its purpose and usage
- Changing workflow patterns → update relevant documentation

---

## For Users Downloading This Template

To customize this workspace to your own needs, fill in your context documents in `context/` and modify as needed. Then use `/create-plan` to plan out and `/implement` to execute any structural changes. This ensures everything stays in sync — especially CLAUDE.md, which must always reflect the current state of the workspace.

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Work**: Use commands or direct Claude with tasks
3. **Plan changes**: Use `/create-plan` before significant additions
4. **Execute**: Use `/implement` to execute plans
5. **Maintain**: Claude updates CLAUDE.md and context/ as the workspace evolves

---

## Notes

- Keep context minimal but sufficient — avoid bloat
- Plans live in `plans/` with dated filenames for history
- Outputs are organized by type/purpose in `outputs/`
- Reference materials go in `reference/` for reuse
