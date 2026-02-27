# Skill: Create Plan

**Purpose**: For each pending task file in `Vault/Needs_Action/` that does not
yet have a corresponding plan, generate a structured `PLAN_<task>.md` file in
`Vault/Plans/`. Plans describe the intended execution strategy before any action
is taken, enabling human review and safe automated processing in later phases.

---

## Inputs

- All `*.md` task files in `./Vault/Needs_Action/` that meet the scan criteria
- YAML frontmatter fields read from each task: `type`, `original_name`,
  `created_at`, `priority`, `needs_human_approval`, `related_artifact`
- Task body text (content below the frontmatter block)
- `./Vault/Plans/` directory — checked to detect pre-existing plans

---

## Outputs

- One new `./Vault/Plans/PLAN_<task_filename>.md` per qualifying task

No other files are created, modified, or moved.

---

## Scan Criteria

When iterating `./Vault/Needs_Action/`, **skip** any file that matches ANY of
the following conditions:

| Condition | Reason |
|-----------|--------|
| `filename == "README.md"` | Folder metadata |
| `filename == "TRIAGE_SUMMARY.md"` | Triage output, not a task |
| `filename` starts with `RESULT_` | Result document, not a task |
| File does not have `.md` extension | Raw staged artifact (`FILE_*` with no extension) |
| `./Vault/Plans/PLAN_<filename>` already exists | Plan already created — do NOT overwrite |

Only files that pass ALL filters are planned.

---

## Procedure

### Step 1 — Inventory pending tasks

1. List all files in `./Vault/Needs_Action/`.
2. Apply the scan criteria above; collect the qualifying task file list.
3. If the list is empty, log `"No new tasks require plans."` and stop.

### Step 2 — For each qualifying task file

#### 2a — Read and parse

1. Read the full file content.
2. Extract YAML frontmatter (between the first pair of `---` delimiters).
3. Parse the following fields:

   | Field | Fallback if missing |
   |-------|---------------------|
   | `type` | `"unknown"` |
   | `original_name` | task filename stem |
   | `created_at` | `"unknown"` |
   | `priority` | `"normal"` |
   | `needs_human_approval` | `false` |
   | `related_artifact` | `""` (empty string) |

4. Extract the body text (everything after the closing `---`). Treat this as
   context for the Objective and Notes sections.

#### 2b — Derive Objective

Write 1–2 sentences that describe what the task is requesting, drawn from:
- The `type` and `original_name` frontmatter fields
- The body text (especially any heading or bullet content)

Do NOT invent information not present in the task file.

#### 2c — Select Execution Strategy

Choose the strategy description based on `type`:

| `type` value | Execution Strategy |
|--------------|--------------------|
| `file_drop` | Read and analyse the artifact at `related_artifact`. Extract key information (content type, subject, any actionable items). Determine whether the task requires external action (financial, communication) or is review-only. Produce a structured result document. |
| `email` | Read the email content from the artifact. Identify sender, subject, and intent. Draft a proposed reply or routing decision. Flag for human approval if any commitment is implied. Produce a draft response document. |
| `meeting` | Read meeting notes from the artifact. Extract action items, decisions, and owners. Produce a structured summary with assigned next steps. |
| `calendar` | Parse the event details. Check for conflicts or required preparation. Produce a preparation checklist. |
| *(anything else)* | Read the task description and artifact (if present). Identify the core request. Apply generic processing: summarise, suggest next steps, flag risks. Produce a result document. |

#### 2d — Compose plan content

Assemble the plan file using the template in the **Plan File Format** section
below. All fields must be populated — no blank sections.

#### 2e — Write the plan file

Write the completed content to:

```
./Vault/Plans/PLAN_<task_filename>
```

Where `<task_filename>` is the exact filename of the task file including its
`.md` extension.

Example: task `FILE_invoice.txt.md` → plan `PLAN_FILE_invoice.txt.md`

Log: `"Plan created: Vault/Plans/PLAN_<task_filename>"`

### Step 3 — Completion summary

After processing all qualifying tasks, log:

```
create_plan complete. Plans created: <N>. Skipped (already planned): <M>.
```

---

## Plan File Format

```
---
task_file: <original task filename, e.g. FILE_invoice.txt.md>
status: draft
created_at: <current ISO 8601 UTC timestamp>
needs_human_approval: <value copied from task frontmatter — true or false>
current_step: 0
---

# Plan for <task_filename>

## Objective
<1-2 sentences derived from task frontmatter and body. Describe what is being
requested and what a successful outcome looks like.>

## Execution Strategy
<Select and adapt from the type-based strategy table above. Name the artifact
file explicitly if related_artifact is present. State clearly whether human
approval is required before execution.>

## Steps
- [ ] Step 1: Validate task metadata (confirm type, priority, needs_human_approval)
- [ ] Step 2: Locate and read related artifact (<artifact filename or "N/A">)
- [ ] Step 3: Analyse artifact content and identify actionable items
- [ ] Step 4: Check if human approval is required (needs_human_approval: <true/false>)
- [ ] Step 5: Prepare result output document
- [ ] Step 6: Mark plan ready for execution

## Notes
<Context-specific observations drawn from the task body and artifact filename.
Include: artifact name, any risk flags from the task body, priority level, and
any task-type-specific considerations. Do NOT add information not present in
the source files.>
```

---

## Safety Constraints

- **Must NOT** modify, move, or delete any task file in `Vault/Needs_Action/`.
- **Must NOT** modify any file in `Vault/Done/`, `Vault/Logs/`, `Dashboard.md`,
  `System_Logs.md`, or `Company_Handbook.md`.
- **Must NOT** overwrite an existing `PLAN_*.md` file. If a plan already exists
  for a task, skip it silently.
- **Must NOT** create any file outside `Vault/Plans/`.
- **Must NOT** execute any action described in the plan (no file moves, no
  external calls, no result document creation).
- **Must NOT** invent or fabricate content not present in the source task file.
- Plan `status` must always be set to `draft` — never `approved` or `ready`.
- `current_step` must always be set to `0` — the orchestrator manages step
  progression in future phases.

---

## Error Handling

- If a task file cannot be read, log a warning and skip it:
  ```
  WARNING: Could not read task file <filename> — skipping.
  ```
- If the YAML frontmatter cannot be parsed, use all fallback values and note
  this in the plan's `## Notes` section:
  ```
  Note: Frontmatter could not be parsed. All fields set to defaults.
  ```
- If `Vault/Plans/` does not exist, create it before writing any plan files.
- Never crash on a single file failure — continue processing remaining tasks.

---

## Success Criteria

- [ ] All qualifying task files in `Vault/Needs_Action/` were scanned
- [ ] Scan criteria filters were applied correctly (no README, TRIAGE_SUMMARY,
  RESULT_*, non-.md, or already-planned tasks were processed)
- [ ] One `PLAN_*.md` was created in `Vault/Plans/` per qualifying task
- [ ] Each plan contains valid YAML frontmatter with all required fields
- [ ] `status` is `draft` and `current_step` is `0` in every plan
- [ ] `needs_human_approval` was copied accurately from the task frontmatter
- [ ] Execution strategy was adapted to the task `type`
- [ ] Artifact filename is mentioned in the plan if `related_artifact` is present
- [ ] No task files were modified, moved, or deleted
- [ ] No existing plan files were overwritten
- [ ] No files were created outside `Vault/Plans/`
