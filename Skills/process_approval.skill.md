# Skill: Process Approval

**Purpose**: Scan `Vault/Approved/` and `Vault/Rejected/` for approval decision
files placed there by the human operator. For each file found, update the
corresponding plan's status accordingly, append an execution or rejection note,
archive the approval file, and write structured log entries.

This skill completes the HITL loop started by `route_for_approval`. After it
runs, approved plans are back to `status: draft` and eligible for `execute_plan`
on the next invocation. Rejected plans are permanently closed.

Invocation is **manual** — this skill does not run autonomously and does not
execute any plan or move any task files.

---

## Inputs

- All files in `./Vault/Approved/` (excluding `README.md`)
- All files in `./Vault/Rejected/` (excluding `README.md`)
- For each approval file: the `plan_file` reference in its YAML frontmatter,
  pointing to a file in `./Vault/Plans/`
- `./Vault/Logs/` directory — to append JSONL records
- `./System_Logs.md` — to append human-readable log entries

---

## Outputs

**For each approved file:**
- Plan file updated in place: `status` → `draft`, `current_step` → `0`
- Approval execution note appended to plan `## Notes` section
- Approval file moved: `./Vault/Approved/<filename>` → `./Vault/Archive/<filename>`
- `./System_Logs.md` — one new log line appended
- `./Vault/Logs/YYYY-MM-DD.jsonl` — one new JSONL record

**For each rejected file:**
- Plan file updated in place: `status` → `complete`, rejection note appended
- Rejection note appended to plan `## Notes` section
- Approval file moved: `./Vault/Rejected/<filename>` → `./Vault/Archive/<filename>`
- `./System_Logs.md` — one new log line appended
- `./Vault/Logs/YYYY-MM-DD.jsonl` — one new JSONL record

No task files (`Vault/Needs_Action/`) are moved, modified, or deleted.

---

## Eligibility Filter

**Vault/Approved/ scan** — skip any file matching ANY condition:

| Condition | Action |
|-----------|--------|
| `filename == "README.md"` | Skip |
| YAML frontmatter missing or unreadable | Skip + log WARNING |
| `plan_file` field missing or empty | Skip + log WARNING |
| Referenced plan file does not exist | Skip + log WARNING |
| Plan `status` ≠ `waiting_approval` | Skip + log WARNING (unexpected state) |
| `./Vault/Archive/<filename>` already exists | Skip + log WARNING (already processed) |

**Vault/Rejected/ scan** — same filter set applied identically.

---

## Procedure

### Step 1 — Inventory decisions

1. List all files in `./Vault/Approved/` (excluding `README.md`). Apply filter. Collect approved list.
2. List all files in `./Vault/Rejected/` (excluding `README.md`). Apply filter. Collect rejected list.
3. If both lists are empty, log `"No approval decisions to process."` and stop.
4. Log: `"Approved items: <N>. Rejected items: <M>. Processing."`

---

### Step 2 — Process each approved item

For each file in the approved list:

#### 2a — Read approval file

Read YAML frontmatter from `./Vault/Approved/<filename>`:
- `plan_file` — path to the plan, e.g. `Vault/Plans/PLAN_FILE_x.md`
- `task_file` — original task filename reference
- `requested_at` — when the approval was originally requested

#### 2b — Update plan frontmatter

Open `./Vault/Plans/<plan_filename>` and rewrite **only** `status` and
`current_step` in the YAML frontmatter block:

```yaml
status: draft
current_step: 0
```

All other frontmatter fields and all body content must be preserved exactly.

#### 2c — Append execution note to plan

Append the following block at the end of the plan file's `## Notes` section
(or at the very end of the file if the Notes section is absent):

```
- **Approval received**: <current ISO timestamp>
  Human operator approved this task. Plan reset to `status: draft` and
  `current_step: 0`. Ready for `execute_plan` invocation.
  Approval file archived: `Vault/Archive/<approval_filename>`
```

#### 2d — Move approval file to Archive

Move `./Vault/Approved/<filename>` → `./Vault/Archive/<filename>`.

If `Vault/Archive/` does not exist, create it first.

#### 2e — Append to System_Logs.md

Under `## Activity Stream`:

```
[YYYY-MM-DD HH:MM] | APPROVAL_PROCESSED | SUCCESS | <plan_filename> approved — reset to draft, ready for execution
```

#### 2f — Append JSONL record

```json
{
  "timestamp": "<current ISO 8601 UTC>",
  "action_type": "approval_processed",
  "actor": "claude_code",
  "approval_file": "Vault/Approved/<filename>",
  "plan_file": "Vault/Plans/<plan_filename>",
  "task_file": "Vault/Needs_Action/<task_file>",
  "decision": "approved",
  "new_plan_status": "draft"
}
```

Log: `"[APPROVAL] <plan_filename> approved → status reset to draft."`

---

### Step 3 — Process each rejected item

For each file in the rejected list:

#### 3a — Read rejection file

Read YAML frontmatter from `./Vault/Rejected/<filename>`:
- `plan_file`, `task_file`, `requested_at` — same fields as approval

#### 3b — Update plan frontmatter

Rewrite **only** `status` in the YAML frontmatter:

```yaml
status: complete
```

`current_step` is left at its current value (was `4` when halted at
`waiting_approval`; set to `4` if the current value is unexpected).

All other frontmatter fields and body content must be preserved exactly.

#### 3c — Append rejection note to plan

Append at the end of the plan's `## Notes` section:

```
- **Rejected**: <current ISO timestamp>
  Human operator rejected this task. Plan marked `status: complete` — no
  further execution will occur. Task file remains in Vault/Needs_Action/
  for manual review and cleanup.
  Rejection file archived: `Vault/Archive/<rejection_filename>`
```

#### 3d — Move rejection file to Archive

Move `./Vault/Rejected/<filename>` → `./Vault/Archive/<filename>`.

#### 3e — Append to System_Logs.md

```
[YYYY-MM-DD HH:MM] | APPROVAL_PROCESSED | REJECTED | <plan_filename> rejected — plan closed, no execution
```

#### 3f — Append JSONL record

```json
{
  "timestamp": "<current ISO 8601 UTC>",
  "action_type": "approval_rejected",
  "actor": "claude_code",
  "approval_file": "Vault/Rejected/<filename>",
  "plan_file": "Vault/Plans/<plan_filename>",
  "task_file": "Vault/Needs_Action/<task_file>",
  "decision": "rejected",
  "new_plan_status": "complete"
}
```

Log: `"[APPROVAL] <plan_filename> rejected → status set to complete. No execution."`

---

### Step 4 — Completion summary

After processing all items, log:

```
process_approval complete.
  Approved and reset to draft : <N>
  Rejected and closed         : <M>
  Skipped (ineligible)        : <K>
  Errors                      : <E>
```

---

## Plan State Transitions (this skill)

```
[waiting_approval] + human moves to Approved/ → [draft]   (eligible for execute_plan)
[waiting_approval] + human moves to Rejected/ → [complete] (terminal — no execution)
```

**Forbidden in this skill:**
- Setting plan status to anything other than `draft` (approved) or `complete` (rejected)
- Executing the plan or invoking any other skill
- Moving task files (`Vault/Needs_Action/`)
- Modifying the result file (`RESULT_*.md`) if it exists

---

## Frontmatter Update Rules

When rewriting plan frontmatter:
1. Locate the opening `---` on line 1.
2. Locate the closing `---` that ends the frontmatter block.
3. Rewrite **only** the `status` field (and `current_step` for approved items).
4. Preserve all other fields byte-for-byte: `task_file`, `created_at`,
   `needs_human_approval`.
5. Preserve all content after the closing `---` byte-for-byte.

Never reconstruct frontmatter from scratch — only modify the target fields.

---

## Safety Constraints

- **Must NOT** execute the plan or trigger `execute_plan` automatically.
- **Must NOT** move task files from `Vault/Needs_Action/`.
- **Must NOT** delete any files — only move approval/rejection files to Archive.
- **Must NOT** overwrite existing files in `Vault/Archive/`.
- **Must NOT** modify `Company_Handbook.md`, watcher scripts, or other skills.
- **Must NOT** modify the RESULT file if one exists in `Vault/Needs_Action/`.
- **Must NOT** process a file whose referenced plan does not exist.
- Approved path sets `status: draft` — never `approved` or `ready`.
- Rejected path sets `status: complete` — never `cancelled` or `deleted`.

---

## Error Handling

- Plan file update fails: log ERROR, do NOT move the approval file, skip.
  Leaves the approval file in `Approved/` or `Rejected/` for retry.
- Archive move fails: log WARNING — plan has already been updated. Flag for
  manual cleanup. Do not revert the plan update.
- JSONL append fails: log WARNING — plan and archive move succeeded. Flag for
  manual log entry.
- Never crash on a single item failure — continue processing remaining items.

Error log format:
```
[YYYY-MM-DD HH:MM] | APPROVAL_PROCESSED | ERROR | <approval_filename> — <brief description>
```

---

## Success Criteria

- [ ] `Vault/Approved/` scanned; eligibility filter applied
- [ ] `Vault/Rejected/` scanned; eligibility filter applied
- [ ] Each approved plan reset to `status: draft`, `current_step: 0`
- [ ] Each rejected plan set to `status: complete`
- [ ] Execution note appended to every approved plan's Notes section
- [ ] Rejection note appended to every rejected plan's Notes section
- [ ] All processed approval files moved to `Vault/Archive/`
- [ ] All processed rejection files moved to `Vault/Archive/`
- [ ] No existing Archive files overwritten
- [ ] `System_Logs.md` appended for every decision processed
- [ ] JSONL record written for every decision processed
- [ ] No task files moved or modified
- [ ] No plan executed automatically
- [ ] Completion summary logged
