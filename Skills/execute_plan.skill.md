# Skill: Execute Plan

**Purpose**: Process eligible plan files from `Vault/Plans/`, execute the work
described in each plan, produce result documents, manage plan state transitions,
and move completed tasks to `Vault/Done/`. This skill bridges plan-based
reasoning with the task-closure behavior established by `close_task`.

Invocation is **manual** — this skill must be explicitly called by a human
operator or the orchestrator. It does not run autonomously.

---

## Inputs

- All `PLAN_*.md` files in `./Vault/Plans/` with `status: draft`
- For each plan: the task file referenced in `task_file` frontmatter field,
  located at `./Vault/Needs_Action/<task_file>`
- The related artifact path from the task file's `related_artifact` frontmatter
  field (e.g. `Needs_Action/FILE_<name>`)
- `./System_Logs.md` (to append log entries)
- `./Vault/Logs/` directory (to append JSONL records)

---

## Outputs

For each plan processed to completion (`needs_human_approval: false`):
- Plan file updated in place: `status` → `complete`, `current_step` → `6`
- `./Vault/Needs_Action/RESULT_<task_file>` — result document (created before move)
- `./System_Logs.md` — one new log line appended
- `./Vault/Logs/YYYY-MM-DD.jsonl` — one new JSONL record appended
- Task file moved: `./Vault/Needs_Action/<task_file>` → `./Vault/Done/<task_file>`
- Result file moved: `./Vault/Needs_Action/RESULT_<task_file>` → `./Vault/Done/RESULT_<task_file>`
- Artifact moved: `./Vault/Needs_Action/<FILE_artifact>` → `./Vault/Archive/<FILE_artifact>` (if present)

For each plan halted for approval (`needs_human_approval: true`):
- Plan file updated in place: `status` → `waiting_approval`, `current_step` → `4`
- `./Vault/Needs_Action/RESULT_<task_file>` — result document written and left in place
- `./System_Logs.md` — one new BLOCKED log line appended
- `./Vault/Logs/YYYY-MM-DD.jsonl` — one new JSONL record with `final_status: waiting_approval`
- Task file remains in `Vault/Needs_Action/` — NOT moved
- Artifact remains in `Vault/Needs_Action/` — NOT moved

---

## Eligibility Filter

When scanning `./Vault/Plans/`, **skip** any plan that matches ANY condition:

| Condition | Action |
|-----------|--------|
| `status` is not `draft` | Skip — only `draft` plans are eligible |
| `status: complete` | Skip — already executed |
| `status: waiting_approval` | Skip — suspended pending human decision |
| `status: in_progress` | Skip — indicates an interrupted prior run; do NOT re-enter |
| `task_file` field is missing or empty | Skip and log a WARNING |
| `./Vault/Needs_Action/<task_file>` does not exist | Skip and log a WARNING |
| `./Vault/Needs_Action/RESULT_<task_file>` already exists | Skip and log a WARNING — never overwrite |

Log a summary of skipped plans before processing begins.

---

## Procedure

### Step 1 — Inventory eligible plans

1. List all files in `./Vault/Plans/` matching the pattern `PLAN_*.md`.
2. For each file, read the YAML frontmatter and apply the eligibility filter.
3. Collect the eligible list. If empty, log `"No eligible plans to execute."` and stop.
4. Log: `"Eligible plans: <N>. Beginning execution."`

---

### Step 2 — For each eligible plan: begin execution

#### 2a — Transition plan to `in_progress`

Update the plan file's frontmatter:
```yaml
status: in_progress
current_step: 1
```

Log: `"[PLAN] <plan_filename> → in_progress (step 1)"`

**State guard**: If the plan file cannot be updated, abort this plan, log ERROR,
and move to the next plan. Never attempt execution with a stale plan state.

---

### Step 3 — Read task and artifact

#### 3a — Read task file

Read `./Vault/Needs_Action/<task_file>` (path from `task_file` frontmatter).
Parse YAML frontmatter: extract `type`, `original_name`, `priority`,
`needs_human_approval`, `related_artifact`, `created_at`.

Update plan: `current_step: 2`

#### 3b — Read artifact (if present)

If `related_artifact` is non-empty, resolve the path relative to the vault root
and attempt to read it. Record whether the artifact was found and readable.
If not found, note this in the result — do NOT error.

Update plan: `current_step: 3`

---

### Step 4 — Generate result document

Create `./Vault/Needs_Action/RESULT_<task_file>` with the following structure:

```
# Processing Result: <task_file>

## Summary
<2–3 sentences describing what the task requested, what artifact was reviewed,
and what the key findings are. Derived from the task body, artifact contents,
and the plan's Objective. Do not invent information.>

## What Was Inspected
- Plan file: Vault/Plans/PLAN_<task_file> (status: in_progress)
- Task file: Vault/Needs_Action/<task_file> (frontmatter parsed)
- Related artifact: <path> (<"contents reviewed" / "not present">)
- Frontmatter: type=<>, priority=<>, needs_human_approval=<>

## Extracted Data
<Key structured information pulled from the artifact. Format varies by type:>
- file_drop: list key fields found (client, amounts, dates, subjects, etc.)
- email: sender, subject, intent, required response
- meeting: action items, decisions, owners
- other: any structured data identifiable from the content

## Risk Assessment
<Identify any risks in the task context. Always check:>
- Financial commitment (invoices, payments, contracts) → flag for human approval
- External communication (emails, messages) → flag for human approval
- Irreversible actions (deletions, sends) → flag for human approval
- If none of the above apply: "No risks requiring escalation identified."

## Recommended Actions
- [ ] <Highest-priority next step>
- [ ] <Second step>
- [ ] <Third step — if approval required, this must be the first item>

## Approval Note
<If needs_human_approval is true:>
  This task requires human approval before any action is taken.
  Task has been left in Vault/Needs_Action/. Plan status set to waiting_approval.
  Human operator must approve by moving the task to Vault/Approved/ or
  reject by moving it to Vault/Rejected/.

<If needs_human_approval is false:>
  No approval required. Task eligible for autonomous processing.
  Proceeding to completion. External actions (if any) flagged in Recommended
  Actions above must still be reviewed by a human before being carried out.

## Completion Note
<Why this task is considered complete in Silver context. Reference: artifact
reviewed, result documented, file lifecycle completed, no external actions
taken.>
```

Update plan: `current_step: 4`

**Safety**: If `./Vault/Needs_Action/RESULT_<task_file>` already exists, abort
this plan, log a WARNING, and move to the next plan. Never overwrite.

---

### Step 5 — Approval gate

Read `needs_human_approval` from the task frontmatter (parsed in Step 3a).

#### If `needs_human_approval: true`

1. Update plan frontmatter:
   ```yaml
   status: waiting_approval
   current_step: 4
   ```
2. Append to `System_Logs.md` under `## Activity Stream`:
   ```
   [YYYY-MM-DD HH:MM] | PLAN_EXECUTION | BLOCKED | <task_file> — waiting human approval
   ```
3. Append JSONL record to `./Vault/Logs/YYYY-MM-DD.jsonl`:
   ```json
   {
     "timestamp": "<ISO UTC>",
     "action_type": "plan_executed",
     "actor": "claude_code",
     "plan_file": "Vault/Plans/PLAN_<task_file>",
     "task_file": "Vault/Needs_Action/<task_file>",
     "final_status": "waiting_approval"
   }
   ```
4. **STOP** — do not move any files. Leave task, result, and artifact in
   `Vault/Needs_Action/`. Move to next plan.

#### If `needs_human_approval: false`

Continue to Step 6.

---

### Step 6 — Move files to Done and Archive

Execute file moves in this order:

1. Move task file:
   `./Vault/Needs_Action/<task_file>` → `./Vault/Done/<task_file>`

2. Move result file:
   `./Vault/Needs_Action/RESULT_<task_file>` → `./Vault/Done/RESULT_<task_file>`

3. Move artifact (best-effort):
   - Resolve artifact filename from `related_artifact` frontmatter field.
   - If `./Vault/Needs_Action/<FILE_artifact>` exists, move it to
     `./Vault/Archive/<FILE_artifact>`.
   - If not present, skip silently — do NOT error.

Update plan: `current_step: 6`

---

### Step 7 — Mark plan complete and write logs

1. Update plan frontmatter:
   ```yaml
   status: complete
   current_step: 6
   ```

2. Append to `System_Logs.md` under `## Activity Stream`:
   ```
   [YYYY-MM-DD HH:MM] | PLAN_EXECUTION | SUCCESS | <task_file> plan executed, result written, moved to Done
   ```

3. Append JSONL record to `./Vault/Logs/YYYY-MM-DD.jsonl`:
   ```json
   {
     "timestamp": "<ISO UTC>",
     "action_type": "plan_executed",
     "actor": "claude_code",
     "plan_file": "Vault/Plans/PLAN_<task_file>",
     "task_file": "Vault/Needs_Action/<task_file>",
     "final_status": "complete"
   }
   ```

Log: `"[PLAN] <plan_filename> → complete"`

---

### Step 8 — Completion summary

After all eligible plans are processed, log:

```
execute_plan complete.
  Executed (complete)        : <N>
  Halted (waiting_approval)  : <M>
  Skipped (ineligible)       : <K>
  Errors                     : <E>
```

---

## Plan State Transition Diagram

```
         [draft]
            │
            │ execution begins
            ▼
       [in_progress]
            │
     ┌──────┴──────┐
     │             │
     │ approval    │ no approval
     │ required    │ required
     ▼             ▼
[waiting_approval] [complete]
```

**Allowed transitions**:
- `draft` → `in_progress`
- `in_progress` → `complete`
- `in_progress` → `waiting_approval`

**Forbidden transitions**:
- Any state → `draft` (plans never regress to draft)
- `waiting_approval` → `complete` (requires human action outside this skill)
- `complete` → any state (terminal)
- Skipping `in_progress` (must always pass through it)

---

## Plan Frontmatter Update Format

When updating a plan file's frontmatter, rewrite **only** the `status` and
`current_step` fields between the `---` delimiters. All other frontmatter
fields (`task_file`, `created_at`, `needs_human_approval`) must be preserved
exactly. All content below the closing `---` must be preserved exactly.

Example — transition to `complete`:
```yaml
---
task_file: FILE_sample_invoice_request.txt.md
status: complete
created_at: 2026-02-27T00:00:00+00:00
needs_human_approval: false
current_step: 6
---
```

---

## Error Handling

- If reading any file fails: log ERROR, mark plan with `status: error` in
  frontmatter, write JSONL record with `"final_status": "error"`, skip to next.
- If writing the RESULT file fails: log ERROR, revert plan to `status: draft`,
  do NOT move any files, skip to next plan.
- If a file move fails mid-sequence (e.g. task moved but result move fails):
  log ERROR with full context. Do NOT attempt to undo the successful moves.
  Leave plan in `status: in_progress` so the operator can inspect the partial
  state.
- Append every error to `System_Logs.md`:
  ```
  [YYYY-MM-DD HH:MM] | PLAN_EXECUTION | ERROR | <plan_filename> — <brief description>
  ```
- Never crash on a single plan failure — continue processing remaining plans.

---

## Safety Constraints

- **Must NOT** overwrite an existing `RESULT_*.md` file.
- **Must NOT** execute external actions (email, payments, API calls, HTTP
  requests).
- **Must NOT** modify `Company_Handbook.md`, `Dashboard.md`, any watcher
  script, or any skill file.
- **Must NOT** modify the task file (read-only). All output goes to RESULT.
- **Must NOT** delete any file — only move.
- **Must NOT** process a plan whose `task_file` field is missing or points to a
  non-existent file.
- **Must NOT** skip the `in_progress` transition — every executed plan must pass
  through it.
- **Must NOT** move files for a plan whose `needs_human_approval` is `true`.
- If `Vault/Archive/` or `Vault/Done/` does not exist, create it before moving.

---

## Integration with `close_task`

This skill supersedes `close_task` for plan-driven tasks. The behavioral
contract is identical in outcome (result doc, logs, Done/Archive moves) but
`execute_plan` adds:

| Addition | Detail |
|----------|--------|
| Plan state management | `status` and `current_step` tracked throughout |
| Approval gate | `waiting_approval` state halts file moves |
| Plan-sourced context | Result document references the plan's Objective and Strategy |
| Batch execution | Processes all eligible plans in one invocation |

`close_task` remains available for direct task processing when no plan exists.

---

## Success Criteria

- [ ] All `PLAN_*.md` files in `Vault/Plans/` were scanned
- [ ] Eligibility filter applied correctly — only `status: draft` plans processed
- [ ] Each eligible plan transitioned through `in_progress` before any other state
- [ ] RESULT file created for every processed plan
- [ ] No existing RESULT file was overwritten
- [ ] `needs_human_approval: true` plans halted at `waiting_approval` — no files moved
- [ ] `needs_human_approval: false` plans: task + result moved to Done, artifact to Archive
- [ ] Plan frontmatter updated correctly at each step transition
- [ ] JSONL record written for every processed plan
- [ ] `System_Logs.md` appended for every processed plan
- [ ] No files deleted
- [ ] No external actions performed
- [ ] Completion summary logged at end
