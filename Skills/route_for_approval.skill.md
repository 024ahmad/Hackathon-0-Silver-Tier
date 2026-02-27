# Skill: Route for Approval

**Purpose**: Scan `Vault/Plans/` for plans with `status: waiting_approval` and
generate a corresponding approval request file in `Vault/Pending_Approval/` for
each one. This surfaces blocked plans to the human operator in a single,
structured location so they can make Approve/Reject decisions.

Invocation is **manual** — this skill must be explicitly called. It does not
run autonomously and does not execute or modify any plan logic.

---

## Inputs

- All `PLAN_*.md` files in `./Vault/Plans/` with `status: waiting_approval`
- `./Vault/Needs_Action/<task_file>` — read to extract summary context
- `./Vault/Pending_Approval/` directory — checked for pre-existing approval files
- `./Vault/Logs/` directory — to append JSONL records

---

## Outputs

- One new `./Vault/Pending_Approval/APPROVAL_<plan_filename>` per qualifying plan
- `./Vault/Logs/YYYY-MM-DD.jsonl` — one JSONL record per approval file created

No other files are created, modified, or moved.

---

## Eligibility Filter

When scanning `./Vault/Plans/`, **skip** any plan that matches ANY condition:

| Condition | Action |
|-----------|--------|
| `status` ≠ `waiting_approval` | Skip silently |
| `task_file` field missing or empty | Skip + log WARNING |
| `./Vault/Pending_Approval/APPROVAL_<plan_filename>` already exists | Skip — do NOT overwrite |

Log a count of skipped plans before processing begins.

---

## Procedure

### Step 1 — Inventory waiting plans

1. List all `PLAN_*.md` files in `./Vault/Plans/`.
2. Read YAML frontmatter for each; apply eligibility filter.
3. Collect qualifying list. If empty, log `"No plans awaiting approval routing."` and stop.
4. Log: `"Plans requiring approval routing: <N>."`

---

### Step 2 — For each qualifying plan: read context

1. Read the plan's frontmatter fields:
   - `task_file` — filename of the blocked task
   - `needs_human_approval` — must be `true` to have reached this state
   - `created_at` — original plan creation timestamp

2. Attempt to read `./Vault/Needs_Action/<task_file>` to extract:
   - `type` from task frontmatter
   - `original_name` from task frontmatter
   - `priority` from task frontmatter
   - First meaningful line(s) of the task body — used as the summary

   If the task file is not present, use the plan's `## Objective` section as
   the summary source instead. Note this in the approval file.

3. Derive `reason_for_approval` from task type:

   | Task `type` | Reason |
   |-------------|--------|
   | `file_drop` | "Task involves a file requiring review before autonomous processing." |
   | `email` | "Task involves external communication requiring human sign-off." |
   | `meeting` | "Task involves meeting action items requiring human confirmation." |
   | `calendar` | "Task involves calendar/scheduling action requiring human review." |
   | *(other)* | "Task flagged for human review prior to execution." |

   Always append: `" Human marked this task as requiring approval
   (needs_human_approval: true)."`

---

### Step 3 — Write approval request file

Write `./Vault/Pending_Approval/APPROVAL_<plan_filename>` using the format
defined in the **Approval Request File Format** section below.

Log: `"Approval file created: Vault/Pending_Approval/APPROVAL_<plan_filename>"`

---

### Step 4 — Append JSONL log record

Append one record to `./Vault/Logs/YYYY-MM-DD.jsonl`:

```json
{
  "timestamp": "<current ISO 8601 UTC>",
  "action_type": "approval_requested",
  "actor": "claude_code",
  "plan_file": "Vault/Plans/<plan_filename>",
  "task_file": "Vault/Needs_Action/<task_file>",
  "approval_file": "Vault/Pending_Approval/APPROVAL_<plan_filename>",
  "status": "pending"
}
```

---

### Step 5 — Completion summary

After processing all qualifying plans, log:

```
route_for_approval complete. Approval files created: <N>. Skipped: <M>.
```

---

## Approval Request File Format

```
---
plan_file: Vault/Plans/<plan_filename>
task_file: Vault/Needs_Action/<task_file>
original_name: <original_name from task frontmatter>
task_type: <type from task frontmatter>
priority: <priority from task frontmatter>
requested_at: <current ISO 8601 UTC timestamp>
status: pending
---

# Approval Request: <plan_filename>

## Summary
<2–3 sentences describing what the task is requesting and what artifact or
action is involved. Derived from task body or plan Objective. Do not invent.>

## Reason for Approval

<reason_for_approval string derived from task type — see Procedure Step 2.>

## Plan Reference

- Plan file: `Vault/Plans/<plan_filename>`
- Current plan status: `waiting_approval`
- Task file: `Vault/Needs_Action/<task_file>`
- Original artifact: `<related_artifact from task frontmatter, or "N/A">`

## Human Decision Required

Move this file to make your decision:

| Decision | Action |
|----------|--------|
| **Approve** | Move this file to `Vault/Approved/` |
| **Reject** | Move this file to `Vault/Rejected/` |
| **Defer** | Leave this file here (it will re-appear in the next triage) |

After moving, run the `process_approval` skill to update plan state.
```

---

## Safety Constraints

- **Must NOT** modify the original plan file in `Vault/Plans/`.
- **Must NOT** modify the task file in `Vault/Needs_Action/`.
- **Must NOT** move any plan or task files.
- **Must NOT** execute the plan or create any result documents.
- **Must NOT** overwrite an existing approval file in `Vault/Pending_Approval/`.
- **Must NOT** create files in any directory other than `Vault/Pending_Approval/`
  and `Vault/Logs/`.
- If `Vault/Pending_Approval/` does not exist, create it before writing.

---

## Error Handling

- If a plan file cannot be read: log WARNING, skip it, continue.
- If the task file referenced in `task_file` is not found: use plan `## Objective`
  as summary source, note this in the approval file, continue.
- If writing the approval file fails: log ERROR with filename and reason, skip,
  continue with remaining plans.
- If appending the JSONL record fails: log WARNING — the approval file itself
  was created; flag this for manual log entry.
- Never crash on a single plan failure — continue processing remaining plans.

---

## Success Criteria

- [ ] All `PLAN_*.md` files in `Vault/Plans/` were scanned
- [ ] Only plans with `status: waiting_approval` were processed
- [ ] No existing approval file was overwritten
- [ ] Each approval file contains valid YAML frontmatter with all required fields
- [ ] `status: pending` set in every approval file
- [ ] `reason_for_approval` was derived from task type
- [ ] JSONL record written for each approval file created
- [ ] No plan files, task files, or other vault files were modified or moved
- [ ] No files created outside `Vault/Pending_Approval/` and `Vault/Logs/`
