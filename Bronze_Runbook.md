# Bronze Runbook

> **Note — Silver Preparation Structure Added**
> Silver structural folders (`Vault/Plans/`, `Vault/Approved/`, `Vault/Rejected/`,
> `Vault/Pending_Approval/`, `Vault/Archive/`) have been created in the Vault.
> **Current behavior remains Bronze manual mode.** HITL folders exist but are
> not yet active — no tasks are automatically routed to them. The Bronze
> workflow below is fully unchanged.

Step-by-step guide for processing vault tasks using Agent Skills.
In Bronze tier, all skills are invoked manually via Claude Code prompts.

## Prerequisites
- Vault structure is in place: `Vault/Inbox/`, `Vault/Needs_Action/`, `Vault/Done/`, `Vault/Logs/`
- Core files exist: `Dashboard.md`, `Company_Handbook.md`, `System_Logs.md`
- The file drop watcher has staged at least one task in `Vault/Needs_Action/`

## Workflow

### Step 1: Triage the Queue

**Skill**: `triage_needs_action`

Scan all pending tasks and produce a summary.

**Prompt to Claude Code**:
```
Read the skill file ./Skills/triage_needs_action.skill.md and execute it.
Scan all *.md task files in ./Vault/Needs_Action/ (excluding README.md,
TRIAGE_SUMMARY.md, and RESULT_*.md), parse their YAML frontmatter,
and write a consolidated summary to ./Vault/Needs_Action/TRIAGE_SUMMARY.md.
```

**Expected output**: `Vault/Needs_Action/TRIAGE_SUMMARY.md` with a table of all pending tasks.

### Step 2: Update the Dashboard

**Skill**: `update_dashboard`

Sync the dashboard with the current queue state.

**Prompt to Claude Code**:
```
Read the skill file ./Skills/update_dashboard.skill.md and execute it.
Read ./Vault/Needs_Action/TRIAGE_SUMMARY.md and update ./Dashboard.md:
set the Status Snapshot counts and populate the Needs Action queue.
Preserve all other sections unchanged.
```

**Expected output**: `Dashboard.md` with accurate counts and queue listing.

### Step 3: Close Each Task

**Skill**: `close_task`

Process and complete individual tasks one at a time.

**Prompt to Claude Code**:
```
Read the skill file ./Skills/close_task.skill.md and execute it
for the task: ./Vault/Needs_Action/<task_filename>.md
Create a RESULT file, append logs, and move task + result to ./Vault/Done/.
```

Repeat for each task listed in the triage summary.

**Expected output per task**:
- `Vault/Done/<task_filename>.md` (moved)
- `Vault/Done/RESULT_<task_filename>.md` (moved)
- New entry in `System_Logs.md`
- New record in `Vault/Logs/YYYY-MM-DD.jsonl`

### Step 4: Final Dashboard Refresh

After all tasks are closed, re-run **Step 1** and **Step 2** to reflect the cleared queue.

## Quick Reference

| Step | Skill | Reads | Writes |
|------|-------|-------|--------|
| 1 | triage_needs_action | Vault/Needs_Action/*.md | Vault/Needs_Action/TRIAGE_SUMMARY.md |
| 2 | update_dashboard | TRIAGE_SUMMARY.md, Dashboard.md | Dashboard.md |
| 3 | close_task | Single task .md, artifact | RESULT.md, System_Logs.md, Vault/Logs/*.jsonl, Vault/Done/ |

## Notes
- In Bronze, the watcher (`Watchers/file_drop_watcher.py`) populates the queue automatically.
- Claude Code acts as the reasoning layer — it reads skills and executes them on demand.
- No orchestrator or cron job is needed at this tier; all invocations are manual.
- Silver and Gold tiers will automate skill invocation via an orchestrator loop.
