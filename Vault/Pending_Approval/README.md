# Vault / Pending_Approval

This folder is the **Human-in-the-Loop (HITL) staging area**.

## Purpose

When a task carries `needs_human_approval: true` in its YAML frontmatter, the
`close_task` skill must NOT close it autonomously. Instead, the task should be
noted as BLOCKED in logs and left for human review.

In a future tier this folder will receive copies of those blocked tasks so the
operator can inspect, approve, or reject them before processing continues.

## Current Status (Bronze Tier)

- The folder exists as a structural placeholder.
- The watcher currently hard-codes `needs_human_approval: false` on all
  generated tasks, so no tasks are routed here yet.
- No automated routing to this folder is implemented in Bronze.

## Future Routing Logic (Silver+)

1. Watcher or orchestrator detects `needs_human_approval: true`.
2. Task file is copied here: `Pending_Approval/<task_filename>.md`.
3. Human reviews and either:
   - Deletes the file (reject / skip), or
   - Moves it back to `Needs_Action/` with `needs_human_approval: false` (approve).
4. Orchestrator resumes processing.

## Contents Policy

- Only task `.md` files with `needs_human_approval: true` belong here.
- Do NOT store credentials, API keys, or sensitive data in this folder.
- Files here are intentionally NOT processed automatically.
