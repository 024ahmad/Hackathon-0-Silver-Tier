# Skill: Update Dashboard

**Purpose**: Read the current triage summary and update `Dashboard.md` so the Status Snapshot and Needs Action queue reflect the actual state of the vault. This keeps the dashboard accurate without requiring a full rewrite.

## Inputs
- `./Vault/Needs_Action/TRIAGE_SUMMARY.md` (produced by `triage_needs_action` skill)
- `./Dashboard.md` (current state)
- `./Vault/Done/` directory (to count recent completions)

## Outputs
- `./Dashboard.md` — updated in place (targeted section edits only)

## Procedure

1. Read `./Vault/Needs_Action/TRIAGE_SUMMARY.md`.
   - Extract total task count and the task list table.
   - If the file does not exist, treat pending count as 0.
2. Count files in `./Vault/Done/` matching `RESULT_*.md` to determine completed-today count (or use the Recently Done section if already populated).
3. Read `./Dashboard.md`.
4. Update **## Status Snapshot**:
   - Set `Pending Tasks:` to the count from triage summary.
   - Set `In Progress:` to 0 (Bronze has no in-progress tracking).
   - Set `Completed Today:` to the count of items in Recently Done.
5. Update **## Needs Action (Queue)**:
   - Replace the content under this heading with a bullet list of pending tasks from the triage summary.
   - Format: `- [ ] <filename> — <type>, priority: <priority>`
   - If no tasks: `- (No pending tasks)`
6. Preserve all other sections (`## In Progress`, `## Recently Done`, `## Notes / Decisions`) exactly as they are.
7. Write the updated `Dashboard.md`.

## Safety Constraints
- **Must NOT** modify any file other than `./Dashboard.md`.
- **Must NOT** delete or move any files.
- **Must NOT** clear or overwrite the `## Recently Done` section.
- **Must NOT** remove content from `## Notes / Decisions`.
- Preserve all existing entries in sections not being updated.

## Success Criteria
- [ ] Status Snapshot counts are accurate
- [ ] Needs Action queue matches the triage summary
- [ ] Recently Done section is preserved unchanged
- [ ] Notes / Decisions section is preserved unchanged
- [ ] No other files were modified
