# Watchers

File system watchers that form the Perception layer of the AI Employee.

## file_drop_watcher.py

Monitors `/Vault/Inbox` for new files and stages them into `/Vault/Needs_Action` with metadata.

### Prerequisites

```bash
pip install watchdog
```

### Running

From the vault root (`Bronze/`):

```bash
python Watchers/file_drop_watcher.py
```

Optional: set polling interval (default 250ms):

```bash
WATCH_INTERVAL_MS=500 python Watchers/file_drop_watcher.py
```

### What It Does

When a file is dropped into `/Vault/Inbox`:

1. Copies it to `/Vault/Needs_Action/FILE_<original_name>`
2. Creates `/Vault/Needs_Action/FILE_<original_name>.md` with YAML frontmatter task metadata
3. Appends an entry to `System_Logs.md` under Activity Stream
4. Writes a JSON record to `/Vault/Logs/YYYY-MM-DD.jsonl`

### Quick Test

1. Start the watcher:
   ```bash
   python Watchers/file_drop_watcher.py
   ```
2. In another terminal, drop a test file:
   ```bash
   echo "Hello Bronze Tier" > Vault/Inbox/test_note.txt
   ```
3. Verify:
   - `Vault/Needs_Action/FILE_test_note.txt` exists (copy of original)
   - `Vault/Needs_Action/FILE_test_note.txt.md` exists (task metadata)
   - `System_Logs.md` has a new Activity Stream entry
   - `Vault/Logs/YYYY-MM-DD.jsonl` has a JSON record
