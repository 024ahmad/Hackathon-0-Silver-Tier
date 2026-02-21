# Skill: Close Task

**Purpose**: Process a single task file from `/Vault/Needs_Action`, produce a result document, log the action, and move the task + result to `/Vault/Done`. This is the core "completion" skill that transitions work from the queue to the archive.

## Inputs
- A single task file path: `./Vault/Needs_Action/<task_filename>.md`
- The related artifact path (from YAML frontmatter `related_artifact` field), if present
- `./System_Logs.md` (to append log entry)
- `./Vault/Logs/` directory (to append JSONL record)

## Outputs
- `./Vault/Needs_Action/RESULT_<task_filename>.md` — processing result document (created before move)
- `./System_Logs.md` — one new log line appended under `## Activity Stream`
- `./Vault/Logs/YYYY-MM-DD.jsonl` — one new JSON record appended
- Task file moved to: `./Vault/Done/<task_filename>.md`
- Result file moved to: `./Vault/Done/RESULT_<task_filename>.md`

## Procedure

1. Read the task file at the given path.
2. Parse YAML frontmatter: extract `type`, `original_name`, `created_at`, `status`, `priority`, `needs_human_approval`, `related_artifact`.
3. If `related_artifact` is specified, read the artifact contents to inform the result.
4. **Create the result file** at `./Vault/Needs_Action/RESULT_<task_filename>.md`:
   ```
   # Processing Result: <task_filename>

   ## Summary
   <2-3 sentence description of what the task is and what was found>

   ## What Was Inspected
   - Task file: <path> (frontmatter parsed)
   - Related artifact: <path> (contents reviewed / not present)
   - Frontmatter: type=<>, priority=<>, status=<>, needs_human_approval=<>

   ## Suggested Next Steps
   - [ ] <actionable step 1>
   - [ ] <actionable step 2>
   - [ ] <actionable step 3>

   ## Risks / Approvals Needed
   - <risk assessment or "None identified">

   ## Completion Note
   <Why this is considered Done in Bronze context>
   ```
5. **Append to System_Logs.md** under `## Activity Stream`:
   ```
   [YYYY-MM-DD HH:MM] | TASK_PROCESSED | SUCCESS | <task_filename> processed, result written, moved to Done
   ```
6. **Append JSONL record** to `./Vault/Logs/YYYY-MM-DD.jsonl`:
   ```json
   {
     "timestamp": "<ISO>",
     "action_type": "task_processed",
     "actor": "claude_code",
     "task_file": "Vault/Needs_Action/<task_filename>",
     "result_file": "Vault/Needs_Action/RESULT_<task_filename>.md",
     "final_location": "Vault/Done/<task_filename>",
     "status": "success"
   }
   ```
7. **Move files** to `./Vault/Done/`:
   - Move `./Vault/Needs_Action/<task_filename>.md` → `./Vault/Done/<task_filename>.md`
   - Move `./Vault/Needs_Action/RESULT_<task_filename>.md` → `./Vault/Done/RESULT_<task_filename>.md`
8. **Do NOT move or delete** the staged artifact (`FILE_*` files). Artifacts stay in `./Vault/Needs_Action/` unless the task explicitly requests removal.

## Error Handling
- If any step fails, log an ERROR entry to `System_Logs.md`:
  ```
  [YYYY-MM-DD HH:MM] | TASK_PROCESSED | ERROR | <task_filename> — <brief error description>
  ```
- Write a JSONL record with `"status": "error"` and an `"error"` field.
- Leave the task file in `./Vault/Needs_Action/` (do not move partially processed tasks).

## Safety Constraints
- **Must NOT** delete any files (only move task + result to Done).
- **Must NOT** move or delete staged artifacts (FILE_* files) unless the task explicitly requires it.
- **Must NOT** perform external actions (email, payments, API calls).
- **Must NOT** modify `Company_Handbook.md`.
- **Must NOT** modify the task file itself (it is read-only; all output goes to RESULT).
- Respect `needs_human_approval`: if `true`, do not close — log a BLOCKED entry instead and leave in queue.

## Success Criteria
- [ ] Task file was read and frontmatter was parsed
- [ ] Related artifact was inspected (if present)
- [ ] RESULT file was created with summary, inspected items, next steps, and completion note
- [ ] System_Logs.md was appended with a TASK_PROCESSED entry
- [ ] JSONL log record was written to Vault/Logs/YYYY-MM-DD.jsonl
- [ ] Task and result files were moved to Vault/Done/
- [ ] No staged artifacts were moved or deleted
- [ ] No external actions were performed
