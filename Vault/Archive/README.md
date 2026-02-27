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
- Original files in `Vault/Inbox/` are untouched (the watcher uses copy2).

## Contents Over Time

Each entry here corresponds to one closed task. The file name retains the
`FILE_` prefix to link it back to the task that processed it.

## Retention

No automated retention policy is implemented in Bronze. Files accumulate until
manually reviewed or removed.
