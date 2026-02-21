# Personal AI Employee — Bronze Tier

A local-first, markdown-driven AI agent system that operates as a Digital Full-Time Employee.

**Hackathon Project | Bronze Tier Implementation | Claude Code + Python + Markdown Vault**

---

## Overview

A Personal AI Employee is an autonomous agent system designed to handle structured tasks on behalf of a human operator. Rather than relying on cloud-hosted workflows or third-party automation platforms, this project takes a local-first approach: all state, tasks, logs, and configuration live in a plain markdown vault managed through VS Code.

The Bronze Tier establishes the foundational architecture. It proves that an AI agent (Claude Code) can perceive incoming work, reason about it using defined skills, and persist all outputs with full traceability — without requiring external services, databases, or cloud infrastructure.

### Why Local-First?

- Full data ownership. Nothing leaves your machine unless you choose to share it.
- No vendor lock-in. The vault is plain text — readable, portable, and version-controllable.
- Transparent state. Every decision, action, and log entry is a file you can inspect.
- Offline-capable. The vault works without an internet connection (watcher and vault operate locally).

---

## Architecture Overview

The system follows a three-layer architecture:

```
┌─────────────────────────────────────────────────────┐
│                   PERCEPTION LAYER                   │
│                                                     │
│   Filesystem Watcher (watchdog)                     │
│   Monitors /Vault/Inbox for new files                │
│   Stages tasks into /Vault/Needs_Action with metadata│
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                   REASONING LAYER                    │
│                                                     │
│   Claude Code + Agent Skills                        │
│   Reads tasks, parses frontmatter, inspects files   │
│   Produces results, updates dashboard, closes tasks │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  PERSISTENCE LAYER                   │
│                                                     │
│   Markdown Vault (VS Code)                          │
│   Dashboard.md ── System_Logs.md ── /Vault/Logs/*.jsonl│
│   /Vault/Needs_Action ── /Vault/Done ── /Vault/Inbox │
└─────────────────────────────────────────────────────┘
```

**Perception**: A Python-based filesystem watcher detects new files dropped into `/Vault/Inbox`, copies them into `/Vault/Needs_Action` with a structured YAML-frontmatter task file, and logs the event.

**Reasoning**: Claude Code reads pending tasks, applies Agent Skills (triage, dashboard update, close), produces result documents, and manages the task lifecycle.

**Persistence**: All state lives in the markdown vault. Human-readable logs go to `System_Logs.md`. Structured audit logs go to `/Vault/Logs/` as JSONL. The dashboard reflects current queue state at all times.

---

## Key Features

- **Local-first markdown vault** — All data stored as plain files. No database, no cloud dependency.
- **Filesystem watcher automation** — Python + watchdog monitors `/Vault/Inbox` and stages tasks automatically.
- **Structured task lifecycle** — Files flow through Inbox, Needs_Action, and Done with full metadata.
- **Skills-based AI logic** — AI behavior is defined in reusable, documented skill files rather than ad-hoc prompts.
- **Dual logging** — Human-readable entries in `System_Logs.md` alongside structured JSONL in `/Vault/Logs/`.
- **Dashboard-driven state** — `Dashboard.md` provides a live snapshot of queue depth, active work, and recent completions.
- **YAML frontmatter metadata** — Every task carries machine-readable fields: type, priority, status, timestamps, and artifact references.
- **Company Handbook governance** — `Company_Handbook.md` defines operational rules the AI must follow, including human-in-the-loop policies.

---

## Project Structure

```
Silver/
├── Vault/                             # Data/state directory
│   ├── Inbox/                         # Drop zone — watcher monitors this
│   ├── Needs_Action/                  # Task queue with staged files and metadata
│   ├── Done/                          # Completed tasks and result documents
│   └── Logs/                          # Structured JSONL audit logs
│       └── YYYY-MM-DD.jsonl
├── Watchers/                          # Perception layer
│   └── file_drop_watcher.py
├── Skills/                            # Agent skill definitions
│   ├── triage_needs_action.skill.md
│   ├── update_dashboard.skill.md
│   └── close_task.skill.md
├── Dashboard.md                       # Live operational dashboard
├── Company_Handbook.md                # AI operational policies
├── System_Logs.md                     # Human-readable activity log
├── Bronze_Runbook.md                  # Step-by-step workflow guide
├── Bronze_Proof_Pack.md               # Validation checklist and evidence
└── pyproject.toml                     # Python project config (uv)
```

---

## How It Works

### 1. File Drop (Perception)

A user drops a file into `/Vault/Inbox/`. The filesystem watcher detects it and:
- Copies the file into `/Vault/Needs_Action/` with a `FILE_` prefix
- Creates a companion `.md` task file with YAML frontmatter (type, timestamp, status, priority)
- Appends a log entry to `System_Logs.md`
- Writes a structured JSONL record to `/Vault/Logs/`

### 2. Triage (Reasoning — Skill: triage_needs_action)

Claude Code scans all pending task files in `/Vault/Needs_Action/`, parses their frontmatter, and writes a consolidated `TRIAGE_SUMMARY.md` with a table of all queued items.

### 3. Dashboard Update (Reasoning — Skill: update_dashboard)

Claude reads the triage summary and updates `Dashboard.md`: pending counts, queue listing, and completion totals. Existing sections (Recently Done, Notes) are preserved.

### 4. Task Closure (Reasoning — Skill: close_task)

For each task, Claude:
- Reads the task file and inspects the related artifact
- Creates a `RESULT_*.md` document with summary, inspection notes, suggested next steps, and a completion rationale
- Appends to `System_Logs.md` and `/Vault/Logs/YYYY-MM-DD.jsonl`
- Moves the task and result files to `/Vault/Done/`

### 5. Post-Close Refresh

The triage and dashboard skills are re-run to reflect the cleared queue.

---

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Claude Code CLI

### Setup

```bash
cd AI_Employee_Vault/Bronze
uv sync
```

### Start the Watcher

```bash
python Watchers/file_drop_watcher.py
```

The watcher will monitor `/Vault/Inbox/` and log all activity to stdout.

### Drop a Test File

In a separate terminal:

```bash
echo "Please review Q1 report" > Vault/Inbox/test_task.txt
```

Observe the watcher output confirming the file was detected and staged.

### Process Tasks via Claude Code

Open Claude Code in the vault root and prompt:

```
Read ./Skills/triage_needs_action.skill.md and execute it.
Then read ./Skills/update_dashboard.skill.md and execute it.
Then read ./Skills/close_task.skill.md and close the task
./Vault/Needs_Action/FILE_test_task.txt.md
```

Or simply:

```
process tasks
```

### Verify

- Check `Vault/Done/` for the task and result files
- Check `Dashboard.md` for the updated Recently Done section
- Check `System_Logs.md` for the new log entry
- Check `Vault/Logs/YYYY-MM-DD.jsonl` for the structured record

---

## Security and Design Principles

- **No credentials in the vault.** Secrets, API keys, and passwords are never stored in markdown files.
- **Local-first privacy.** All data stays on the local filesystem. Nothing is transmitted externally.
- **Append-only logging.** Log files are never overwritten or truncated. New entries are appended.
- **Human-in-the-loop.** The Company Handbook prohibits payments, emails to unknown recipients, and irreversible actions without explicit human approval.
- **Read-only task files.** The AI never modifies the original task; all output goes to separate result documents.
- **No external actions in Bronze.** The system does not send emails, make API calls, or interact with external services.

---

## Bronze Tier Scope

### Included

- Vault folder structure with clear lifecycle stages
- One filesystem watcher (file drop detection)
- Three Agent Skills (triage, dashboard, close)
- YAML frontmatter-based task metadata
- Human-readable and structured JSONL logging
- Dashboard state management
- Company Handbook governance rules
- Bronze Runbook with step-by-step instructions
- Proof Pack with validation checklist

### Not Included (planned for higher tiers)

- MCP server integration
- Multiple watchers (Gmail, Calendar, Slack)
- Automated orchestrator loop
- External API actions (LinkedIn, email, payments)
- Odoo or ERP integration
- Multi-agent coordination

---

## Roadmap

### Silver Tier

- Multiple watchers (Gmail, Google Calendar, WhatsApp)
- MCP server for external tool access
- Automated orchestrator loop (watcher-triggered processing)
- LinkedIn posting skill
- Multi-step task chains

### Gold Tier

- Odoo ERP integration
- Cross-domain task routing
- Multi-agent collaboration
- Full approval workflow engine
- Production deployment configuration

---

## Hackathon Submission

| Field | Value |
|---|---|
| Tier | Bronze |
| Reasoning Engine | Claude Code (Anthropic) |
| Vault Format | Markdown (VS Code) |
| Watcher | Python 3.13 + watchdog |
| Package Manager | uv |
| External Dependencies | None (local-first) |

---

## License

This project was built as a hackathon submission. See repository root for license details.

---

Built with Claude Code. Local-first. No cloud required.
"# Hackthon-0-Bronze-Tier" 
"# Hackathon-0-Silver-Tier" 
