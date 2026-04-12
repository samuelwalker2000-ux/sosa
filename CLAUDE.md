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
└── scripts/               # Automation scripts
    ├── send_market_report.py  # Emails latest report via SMTP
    ├── .env.example           # Credential template (copy to .env, never commit)
    └── README.md              # Setup instructions for email delivery
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

**Purpose:** Generate today's comprehensive daily market intelligence report (crypto, macro, AI).

Uses live web search to fetch all data points — no estimates or guesses. Produces a 12-section report covering macro indicators, BTC deep dive, top gainers/losers, setups, unlocks, trade ideas, and a 30-day events calendar. After generating:
1. Saves report to `outputs/market-reports/YYYY-MM-DD-market-report.md`
2. Uploads to Google Drive (folder: "Market Reports")
3. Emails report to samuelwalker2000@gmail.com via `scripts/send_market_report.py`

Run manually any time, or triggered automatically each morning at 7:00 AM EST by the Claude Code scheduler.

**Prerequisite:** `scripts/.env` must be configured with Gmail App Password credentials. See `scripts/README.md`.

---

## Scripts

### scripts/send_market_report.py

Reads the most recent file from `outputs/market-reports/` and sends it via SMTP email to samuelwalker2000@gmail.com.

**Setup:** Copy `scripts/.env.example` to `scripts/.env` and fill in `SMTP_PASSWORD` with a Gmail App Password.

**Run manually:**
```bash
python scripts/send_market_report.py
```

See `scripts/README.md` for full setup instructions.

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
