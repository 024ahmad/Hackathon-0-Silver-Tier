# Vault / Pending_Approval

This folder is the **Human-in-the-Loop (HITL) staging area** for tasks that
require explicit human review before the AI Employee may act on them.

## Purpose

When a task carries `needs_human_approval: true` in its YAML frontmatter, the
`close_task` skill must NOT close it autonomously. The task is instead routed
here and a BLOCKED log entry is written. Processing is suspended until the
human makes a decision.

## Decision Options

| Decision | Action |
|----------|--------|
| **Approve** | Move the task file to `Vault/Approved/` |
| **Reject** | Move the task file to `Vault/Rejected/` |
| **Defer** | Leave the file here; it will appear in the next triage run |

## Lifecycle

```
Vault/Needs_Action/<task>.md  (needs_human_approval: true)
        ↓  (close_task skill detects flag → logs BLOCKED)
Vault/Pending_Approval/<task>.md
        ↓  (human decides)
   ├── Vault/Approved/<task>.md   → orchestrator re-queues for processing
   └── Vault/Rejected/<task>.md   → orchestrator logs rejection, no action
```

## Contents Policy

- Only task `.md` files with `needs_human_approval: true` belong here.
- Do NOT store credentials, artifacts, or result files here.
- Files awaiting decision are not modified by the AI Employee.

## Current Status (Silver Preparation)

Folder is in place as part of Silver structural preparation. The watcher
currently hard-codes `needs_human_approval: false` on all generated tasks,
so no tasks are automatically routed here yet. Automated routing and
orchestrator detection are planned for active Silver implementation.
