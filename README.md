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

## Approval Routing System (Silver Phase 5)

Phase 5 closes the Human-in-the-Loop circuit. Plans halted at
`waiting_approval` by `execute_plan` are now surfaced to the operator as
structured approval request files, and the operator's decision is processed
back into the plan state automatically.

### Two New Skills

#### `route_for_approval`

Scans `Vault/Plans/` for all plans with `status: waiting_approval` and
generates one `APPROVAL_<plan_filename>` file in `Vault/Pending_Approval/`
per qualifying plan. Each approval file contains:

- YAML frontmatter: `plan_file`, `task_file`, `original_name`, `task_type`,
  `priority`, `requested_at`, `status: pending`
- A human-readable summary derived from the task body or plan Objective
- A reason-for-approval string adapted to the task type
- A decision table telling the operator exactly where to move the file

The skill does **not** modify any plan file. It only writes to
`Vault/Pending_Approval/` and `Vault/Logs/`.

#### `process_approval`

Scans `Vault/Approved/` and `Vault/Rejected/` for files placed there by the
operator. For each file found, it reads the `plan_file` reference and updates
the plan accordingly:

| Human action | Plan transition | Effect |
|-------------|----------------|--------|
| Move to `Vault/Approved/` | `waiting_approval` → `draft` | Plan re-eligible for `execute_plan`; approval note appended |
| Move to `Vault/Rejected/` | `waiting_approval` → `complete` | Plan permanently closed; rejection note appended |

In both cases the approval/rejection file is moved to `Vault/Archive/` and
a JSONL record is written with `action_type: "approval_processed"` or
`"approval_rejected"`.

### What Does NOT Happen in This Phase

- `process_approval` does **not** invoke `execute_plan` automatically.
- No task files in `Vault/Needs_Action/` are moved.
- After an approval is processed, the operator must manually invoke
  `execute_plan` (or the orchestrator's hook must be wired — next phase).

### Full HITL Flow (Silver Phase 5 complete)

```
execute_plan detects needs_human_approval: true
        ↓
Plan → waiting_approval
        ↓
route_for_approval creates APPROVAL_* in Vault/Pending_Approval/
        ↓
Human moves file to Vault/Approved/ or Vault/Rejected/
        ↓
process_approval reads decision:
  Approved → plan back to draft  → execute_plan can now close the task
  Rejected → plan set to complete → task remains in Needs_Action for cleanup
```

### Logging

Every routing and processing event appends:
- A line to `System_Logs.md`
- A JSONL record to `Vault/Logs/YYYY-MM-DD.jsonl` with `action_type`:
  `"approval_requested"` / `"approval_processed"` / `"approval_rejected"`

---

## Plan Execution Engine (Silver Phase 4)

Phase 4 introduces `execute_plan` — the skill that drives plans through to
completion. Plans created in Phase 3 (`status: draft`) are now executable.

### What `execute_plan` Does

When invoked, the skill scans `Vault/Plans/` for all `PLAN_*.md` files with
`status: draft` and processes each one in sequence:

1. Transitions plan to `in_progress` (step tracked via `current_step`)
2. Reads the referenced task file and its artifact from `Vault/Needs_Action/`
3. Generates a structured `RESULT_<task_file>` document with extracted data,
   risk assessment, and recommended actions
4. Hits the **approval gate** — checks `needs_human_approval` from task frontmatter
5. Routes to completion or suspension based on the gate result

### Plan State Transitions

```
[draft] → [in_progress] → [complete]
                       ↘ [waiting_approval]
```

Every plan must pass through `in_progress`. No state may be skipped.
`complete` and `waiting_approval` are terminal for this skill — they require
either no further action or a human decision.

### Approval Gating

| `needs_human_approval` | Outcome |
|------------------------|---------|
| `false` | Task + result moved to `Vault/Done/`, artifact to `Vault/Archive/`, plan → `complete` |
| `true` | Result written but files left in place, plan → `waiting_approval`, BLOCKED log written |

Tasks halted at `waiting_approval` are resolved by the human operator moving
the task file to `Vault/Approved/` or `Vault/Rejected/`. The orchestrator
will re-queue approved tasks in a future phase.

### Artifact Archival

On successful completion, the staged `FILE_*` artifact in `Vault/Needs_Action/`
is moved to `Vault/Archive/`. This is best-effort — if the artifact is absent
the step is silently skipped.

### Logging

Every executed plan (complete or waiting_approval) appends:
- A human-readable line to `System_Logs.md`
- A structured JSONL record to `Vault/Logs/YYYY-MM-DD.jsonl` with fields:
  `action_type: "plan_executed"`, `plan_file`, `task_file`, `final_status`

### Invocation

Still **manual** — the operator prompts Claude Code:

```
Read ./Skills/execute_plan.skill.md and execute it.
```

Automated invocation via the orchestrator's `_hook_execute_plan` is the next
phase.

### Integration with `close_task`

`execute_plan` produces identical outcomes to `close_task` (result doc, Done
move, Archive move, logs) but adds plan state tracking, the approval gate, and
batch processing across all eligible plans. `close_task` remains available for
direct task processing when no plan exists.

---

## Plan-Based Execution (Silver Phase 3)

Starting in Phase 3, every task receives a structured **plan file** before any
execution occurs. This introduces a deliberate review layer between task
detection and task processing.

### How It Works

When the `create_plan` skill is invoked (manually or by the orchestrator in a
future phase), it scans `Vault/Needs_Action/` and for each pending task that
does not yet have a plan, it writes:

```
Vault/Plans/PLAN_<task_filename>.md
```

### Plan File Structure

Each plan contains YAML frontmatter and six structured sections:

```yaml
---
task_file: FILE_example.txt.md
status: draft
created_at: 2026-02-27T00:00:00+00:00
needs_human_approval: false
current_step: 0
---
```

Followed by: **Objective**, **Execution Strategy**, **Steps** (checklist),
and **Notes** (contextual observations from the task content).

### Contextual Adaptation

The `Execution Strategy` section is adapted to the task's `type` field:

| Task type | Strategy |
|-----------|---------|
| `file_drop` | Analyse artifact, extract key fields, flag financial/external risks |
| `email` | Draft response plan, identify intent, flag approval requirements |
| `meeting` | Extract action items, decisions, owners |
| *(other)* | Generic processing: summarise, suggest steps, flag risks |

### What Does NOT Happen in This Phase

- Plans are not executed automatically.
- Task files are not modified or moved.
- Claude is not called by the orchestrator.
- Plans with `status: draft` are inert — they are human-reviewable documents
  only.

### Next Phase

Phase 4 will wire the orchestrator's `_hook_execute_plan` to invoke
`close_task` for each plan whose task does not require human approval,
completing the autonomous processing loop.

---

## Silver Orchestrator Framework (Phase 2)

The orchestrator has been upgraded from a Bronze stub to a full Silver state
monitor. It is the execution backbone for future phases — but in this phase it
**only observes and reports**.

### What the Orchestrator Does Now

Every 5 seconds it scans all active Vault state folders and prints a structured
status block:

```
2026-02-27 14:00:00 | INFO    | ----------------------------------------
2026-02-27 14:00:00 | INFO    | [ORCHESTRATOR STATUS]
2026-02-27 14:00:00 | INFO    | Pending Tasks    : 2
2026-02-27 14:00:00 | INFO    | Active Plans     : 0
2026-02-27 14:00:00 | INFO    | Waiting Approval : 1
2026-02-27 14:00:00 | INFO    | Approved         : 0
2026-02-27 14:00:00 | INFO    | Rejected         : 0
2026-02-27 14:00:00 | INFO    | ----------------------------------------
2026-02-27 14:00:00 | INFO    |   Pending tasks:
2026-02-27 14:00:00 | INFO    |     → FILE_q1_report.txt.md
2026-02-27 14:00:00 | INFO    |     → FILE_contract_draft.txt.md
2026-02-27 14:00:00 | INFO    |   Waiting approval:
2026-02-27 14:00:00 | INFO    |     → FILE_payment_request.txt.md
```

### State Detection Functions

Five helper functions return typed `list[Path]` results — no side effects:

| Function | Scans |
|----------|-------|
| `get_pending_tasks()` | `Vault/Needs_Action/*.md` (excl. metadata) |
| `get_active_plans()` | `Vault/Plans/*.md` |
| `get_pending_approvals()` | `Vault/Pending_Approval/` |
| `get_approved_items()` | `Vault/Approved/` |
| `get_rejected_items()` | `Vault/Rejected/` |

### Future Execution Hooks

Three `_hook_*` functions exist as placeholders with detailed TODO comments.
They accept the relevant file lists and currently do nothing (`pass`):

- `_hook_create_plan(pending)` — will invoke plan-writing skill for unplanned tasks
- `_hook_execute_plan(plans)` — will invoke `close_task` skill for approved plans
- `_hook_approval_processing(approved)` — will re-queue approved tasks into `Needs_Action`

These will be wired to Claude in the next Silver phase.

### What It Does NOT Do

- Does not invoke Claude or any skill.
- Does not move, create, or modify any file.
- Does not read file contents — only file names and existence.

### Running the Orchestrator

```bash
python orchestrator.py
```

Shut down cleanly with `Ctrl+C`. The shutdown handler confirms no files were
modified during the session.

---

## Silver Tier Structural Preparation

This phase adds the folder scaffolding and governance structure required for
Silver tier automation. **No existing behavior is changed.** The Bronze manual
workflow remains fully functional.

### Plans Folder (`Vault/Plans/`)

Introduces a dedicated location for `PLAN_<task>.md` files. Before executing
a multi-step task, the Silver orchestrator will write a structured plan here
for inspection. Plans describe intended steps, expected outputs, and approval
requirements before any action is taken.

### Enforced HITL Folder Separation

The single `Pending_Approval/` folder from Bronze is now part of a three-folder
HITL pipeline:

| Folder | Role |
|--------|------|
| `Vault/Pending_Approval/` | Tasks blocked on human decision |
| `Vault/Approved/` | Human-approved; orchestrator re-queues for processing |
| `Vault/Rejected/` | Human-rejected; orchestrator logs and takes no action |

This separation makes approval state unambiguous and machine-readable: the
folder a file lives in IS its approval status.

### Archive Folder (`Vault/Archive/`)

`FILE_*` artifacts are moved here by `close_task` after their tasks complete.
Active since the Bronze Stabilization phase. Keeps `Needs_Action/` clean and
retains original inputs for audit without deletion.

### Behavior in This Phase

All folders are structural placeholders. The watcher, skills, and orchestrator
stub are unchanged. Automated routing into `Pending_Approval/`, `Approved/`,
and `Rejected/` is not yet implemented — it will be wired in active Silver
implementation.

---

## Bronze Stabilization Enhancements

The following structural improvements were added after the initial Bronze implementation to harden safety, improve hygiene, and lay groundwork for Silver tier automation. Existing behavior is fully preserved.

### DRY_RUN Mode (Watcher)

The watcher now reads a `DRY_RUN` environment variable (default: `true`). When enabled, the watcher detects file events and logs exactly what it would do — but writes no files to disk. This makes it safe to run in any environment without side effects during testing or CI.

To enable live mode, set `DRY_RUN=false` (in `.env` or as an environment variable before starting the watcher).

### Vault/Archive Folder

A new `Vault/Archive/` directory receives `FILE_*` artifacts after their tasks are closed. Previously, staged artifacts accumulated in `Vault/Needs_Action/` indefinitely. Now the `close_task` skill moves them to `Archive/` as a best-effort step (skipped silently if the file is absent). No files are ever deleted.

### Vault/Pending_Approval Folder

A new `Vault/Pending_Approval/` directory serves as the structural foundation for the Human-in-the-Loop (HITL) workflow. Tasks with `needs_human_approval: true` in their frontmatter are intended to be routed here for human review before processing can continue. The folder and its policy are in place; automated routing is planned for Silver tier.

### Orchestrator Stub (`orchestrator.py`)

A minimal `orchestrator.py` script polls `Vault/Needs_Action/` every 5 seconds and reports how many pending task files exist. It does not invoke Claude or process tasks — it is a safe scaffold that confirms the polling loop works and establishes the pattern that the Silver tier orchestrator will build on.

```bash
python orchestrator.py
```

### .env.example

A `.env.example` file documents all supported environment variables (`WATCH_INTERVAL_MS`, `DRY_RUN`). The real `.env` file is gitignored and must never be committed.

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
