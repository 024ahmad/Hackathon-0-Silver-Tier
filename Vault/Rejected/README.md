# Vault / Rejected

This folder holds tasks that have been **explicitly rejected by a human operator**.
Rejected tasks are not processed by the AI Employee.

## Purpose

When a human reviews a task in `Vault/Pending_Approval/` and decides it should
not proceed, they move the task file here. The task is then considered closed
with a REJECTED status — no result is written, no action is taken.

## Lifecycle

```
Vault/Pending_Approval/<task>.md
        ↓  (human rejects — moves file here)
Vault/Rejected/<task>.md
        ↓  (orchestrator logs the rejection, no further action)
```

## What Happens on Rejection

- The orchestrator (Silver+) logs a `REJECTION` entry to `System_Logs.md`.
- A structured JSONL record is appended to `Vault/Logs/YYYY-MM-DD.jsonl`
  with `"status": "rejected"`.
- The original artifact (`FILE_*`) stays in `Vault/Needs_Action/` or
  `Vault/Archive/` — it is not deleted.
- No `RESULT_*.md` file is created for rejected tasks.

## Contents Policy

- Only rejected task `.md` files belong here.
- Files are kept permanently for audit purposes — do NOT delete them.
- Do NOT place result files, artifacts, or credentials in this folder.

## Current Status (Silver Preparation)

Folder is created as part of Silver structural preparation.
Orchestrator rejection logging is not yet active.
