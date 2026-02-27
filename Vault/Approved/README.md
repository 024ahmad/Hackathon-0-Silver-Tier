# Vault / Approved

This folder holds tasks that have been **explicitly approved by a human operator**
and are cleared for autonomous processing by the AI Employee.

## Purpose

Tasks routed to `Vault/Pending_Approval/` wait for a human decision. When the
operator approves a task, they move (or the orchestrator moves) the task file
here. The orchestrator then picks it up and re-queues it in `Vault/Needs_Action/`
with `needs_human_approval: false` so the `close_task` skill can process it.

## Lifecycle

```
Vault/Pending_Approval/<task>.md
        ↓  (human approves — moves file here)
Vault/Approved/<task>.md
        ↓  (orchestrator detects and re-queues)
Vault/Needs_Action/<task>.md  ← needs_human_approval set to false
        ↓
Vault/Done/
```

## Contents Policy

- Only approved task `.md` files belong here.
- Do NOT modify the task frontmatter here — the orchestrator handles re-queuing.
- Files here are transient: once re-queued by the orchestrator, they are moved
  to `Vault/Done/` as part of normal task closure.

## Current Status (Silver Preparation)

Folder is created as part of Silver structural preparation.
Automated orchestrator routing is not yet active.
Human operators can manually move files here as a placeholder workflow.
