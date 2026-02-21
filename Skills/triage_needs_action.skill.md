# Skill: Triage Needs Action

**Purpose**: Scan all task files in `/Vault/Needs_Action`, extract metadata from YAML frontmatter, and produce a consolidated triage summary. This gives the AI Employee (and human operators) a quick overview of the pending work queue without modifying any task files.

## Inputs
- All `*.md` files in `./Vault/Needs_Action/` (excluding `README.md` and any `TRIAGE_SUMMARY.md`)
- YAML frontmatter fields: `type`, `original_name`, `created_at`, `status`, `priority`, `needs_human_approval`, `related_artifact`

## Outputs
- `./Vault/Needs_Action/TRIAGE_SUMMARY.md` — created or refreshed (full rewrite on each run)

## Procedure

1. List all `.md` files in `./Vault/Needs_Action/`.
2. Filter out `README.md`, `TRIAGE_SUMMARY.md`, and any `RESULT_*.md` files.
3. For each remaining task file:
   a. Read the file contents.
   b. Parse YAML frontmatter (between `---` delimiters).
   c. Extract: `type`, `original_name`, `created_at`, `status`, `priority`, `needs_human_approval`, `related_artifact`.
   d. If a `related_artifact` path exists, verify the file is present; note if missing.
4. Write `./Vault/Needs_Action/TRIAGE_SUMMARY.md` with the following structure:

   ```
   # Triage Summary
   Generated: <ISO timestamp>
   Total tasks: <count>

   ## Task List
   | # | File | Type | Priority | Status | Human Approval | Created |
   |---|------|------|----------|--------|----------------|---------|
   | 1 | <filename> | <type> | <priority> | <status> | <yes/no> | <date> |

   ## Details
   ### <filename>
   - Original name: ...
   - Related artifact: ... (present / missing)
   - Notes: ...
   ```

5. Log a confirmation message to stdout.

## Safety Constraints
- **Must NOT** delete, move, or modify any task files.
- **Must NOT** modify any files outside `./Vault/Needs_Action/`.
- **Must NOT** create files in any other directory.
- **Must NOT** execute external commands or network calls.
- Only `TRIAGE_SUMMARY.md` may be written; all other files are read-only.

## Success Criteria
- [ ] All `*.md` task files in `./Vault/Needs_Action/` were scanned
- [ ] YAML frontmatter was parsed correctly for each task
- [ ] `TRIAGE_SUMMARY.md` was written with accurate counts and metadata
- [ ] No task files were modified, moved, or deleted
- [ ] Related artifacts were checked for existence
