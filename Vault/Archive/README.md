# Vault / Archive

This folder stores **processed FILE_* artifacts** after their associated tasks
have been completed and moved to `Vault/Done/`.

## Purpose

When the `close_task` skill finishes processing a task, the staged artifact
(e.g. `FILE_team_meeting_notes.txt`) is moved here from `Vault/Needs_Action/`.
This keeps `Needs_Action/` clean while preserving the original file for audit
and reference purposes.

## Move Policy

- Only `FILE_*` files (staged copies of Inbox originals) are moved here.
- The task `.md` file and `RESULT_*.md` file go to `Vault/Done/` — not here.
- Files are **moved, never deleted** — no data is lost.
- Original files in `Vault/Inbox/` are untouched (the watcher uses `copy2`).

## Retention

No automated retention policy is implemented. Files accumulate until manually
reviewed or removed by the operator.

## Current Status (Silver Preparation)

Folder is active. The `close_task` skill moves artifacts here as a best-effort
step on task completion (silently skipped if the artifact is not present).
