# Vault / Plans

This folder stores **structured execution plans** for tasks that require
multi-step reasoning before action is taken.

## Purpose

When the Silver tier orchestrator or a skill determines that a task needs a
plan before execution, it writes a `PLAN_<task_filename>.md` file here.
The plan describes the intended steps, tool calls, expected outputs, and
any approval requirements — before any action is taken.

## File Naming Convention

```
PLAN_<task_filename>.md
```

Example: `PLAN_FILE_q1_report.txt.md`

## Lifecycle

```
Vault/Needs_Action/<task>.md
        ↓  (skill: plan_task)
Vault/Plans/PLAN_<task>.md
        ↓  (human reviews or orchestrator proceeds)
Vault/Needs_Action/<task>.md  ← re-queued with plan reference
        ↓  (skill: close_task with plan)
Vault/Done/
```

## Contents Policy

- Only `PLAN_*.md` files belong here.
- Plans are read-only once written — revisions create new versions.
- Do NOT store credentials, artifacts, or result files here.
- Plans are not deleted; superseded plans remain for audit.

## Current Status (Silver Preparation)

Folder is created as part of Silver structural preparation.
No plan-writing skill is active yet. This folder will be populated
when the Silver orchestrator loop is implemented.
