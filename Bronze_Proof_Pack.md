# Bronze Tier — Proof Pack

Validation date: 2026-02-19

## Requirements Checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Vault folders exist (Vault/Inbox, Vault/Needs_Action, Vault/Done, Vault/Logs) | ✅ |
| 2 | Core files exist (Dashboard.md, Company_Handbook.md, System_Logs.md) | ✅ |
| 3 | One filesystem watcher exists (Watchers/file_drop_watcher.py) | ✅ |
| 4 | Claude can read from Vault/Needs_Action, write outputs, update Dashboard/logs, move to Vault/Done | ✅ |
| 5 | AI functionality implemented as Agent Skills (Skills/) | ✅ |
| 6 | Bronze Runbook documents the manual workflow | ✅ |

## Watcher Command

From the vault root (`Bronze/`):

```bash
python Watchers/file_drop_watcher.py
```

## Demo Steps (1–2 minutes for a judge)

### 1. Start the watcher (~10 seconds)
```bash
cd AI_Employee_Vault/Bronze
python Watchers/file_drop_watcher.py
```

### 2. Drop a file into Inbox (~10 seconds)
In a second terminal:
```bash
echo "Please review Q1 report" > Vault/Inbox/q1_review.txt
```
Observe the watcher log output confirming detection and staging.

### 3. Verify staged task (~15 seconds)
```bash
ls Vault/Needs_Action/
# Expect: FILE_q1_review.txt, FILE_q1_review.txt.md
```

### 4. Stop the watcher
Press `Ctrl+C` in the watcher terminal.

### 5. Run Bronze workflow via Claude Code (~60 seconds)
Prompt Claude Code with:
```
Read ./Skills/triage_needs_action.skill.md and execute it.
Then read ./Skills/update_dashboard.skill.md and execute it.
Then read ./Skills/close_task.skill.md and close the task
./Vault/Needs_Action/FILE_q1_review.txt.md
```

### 6. Verify completion (~15 seconds)
- Check `Vault/Done/` for the task + result files
- Check `Dashboard.md` for updated Recently Done
- Check `System_Logs.md` for the new log entry
- Check `Vault/Logs/YYYY-MM-DD.jsonl` for the JSON record

## Evidence Snippets

### Dashboard — Recently Done
```
- [2026-02-19 13:50] | DEMO_TASK_FileDrop_Review.md — Demo task processed via Bronze skill workflow, moved to Done
- [2026-02-19 13:33] | FILE_sample_invoice_request.txt.md — Invoice request reviewed, next steps documented, moved to Done
- [2026-02-19 13:33] | FILE_team_meeting_notes.txt.md — Meeting notes file reviewed (test/placeholder), moved to Done
```

### System_Logs.md — Latest Entry
```
[2026-02-19 13:50] | TASK_PROCESSED | SUCCESS | DEMO_TASK_FileDrop_Review.md processed, result written, moved to Done
```

### JSONL Log — Latest Record
```json
{"timestamp": "2026-02-19T08:50:30.000000+00:00", "action_type": "task_processed", "actor": "claude_code", "task_file": "Needs_Action/DEMO_TASK_FileDrop_Review.md", "result_file": "Needs_Action/RESULT_DEMO_TASK_FileDrop_Review.md", "final_location": "Done/DEMO_TASK_FileDrop_Review.md", "status": "success"}
```

## Vault Structure

```
Silver/
├── Vault/                           ← Data/state directory
│   ├── Inbox/                       ← Drop zone (watcher monitors this)
│   ├── Needs_Action/                ← Task queue (watcher stages here)
│   ├── Done/                        ← Completed tasks archive
│   └── Logs/                        ← Structured JSONL audit logs
├── Watchers/                        ← Filesystem watcher (perception layer)
│   ├── file_drop_watcher.py
│   └── README.md
├── Skills/                          ← Agent skill definitions
│   ├── triage_needs_action.skill.md
│   ├── update_dashboard.skill.md
│   └── close_task.skill.md
├── Bronze_Proof_Pack.md             ← This file
├── Bronze_Runbook.md                ← Manual workflow guide
├── Company_Handbook.md              ← Operational policies
├── Dashboard.md                     ← Live operational dashboard
├── System_Logs.md                   ← Human-readable activity log
├── main.py
└── pyproject.toml
```
