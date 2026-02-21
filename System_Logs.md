# System Logs

This file captures high-level human-readable logs of AI Employee activity.
Detailed structured logs will be stored in /Vault/Logs/ as JSON files in later tiers.

## Log Format
Each entry must follow this structure:

[YYYY-MM-DD HH:MM] | ACTION_TYPE | STATUS | SHORT_DESCRIPTION

Example:
[2026-01-07 10:45] | TASK_PROCESSED | SUCCESS | Invoice request moved to Done

## Activity Stream
[2026-02-21 12:55] | FILE_DROP_DETECTED | SUCCESS | test_notes.md staged to Needs_Action

[2026-02-19 14:06] | FILE_DROP_DETECTED | SUCCESS | test_note.txt staged to Needs_Action

[2026-02-19 13:33] | FILE_DROP_DETECTED | SUCCESS | team_meeting_notes.txt staged to Needs_Action
[2026-02-19 13:33] | TASK_PROCESSED | SUCCESS | FILE_sample_invoice_request.txt.md processed, result written, moved to Done
[2026-02-19 13:33] | TASK_PROCESSED | SUCCESS | FILE_team_meeting_notes.txt.md processed, result written, moved to Done
[2026-02-19 13:50] | TASK_PROCESSED | SUCCESS | DEMO_TASK_FileDrop_Review.md processed, result written, moved to Done
[2026-02-19 14:10] | TASK_PROCESSED | SUCCESS | FILE_test_note.txt.md processed, result written, moved to Done
[2026-02-21 12:00] | TASK_PROCESSED | SUCCESS | FILE_test_notes.md.md processed, result written, moved to Done


