"""
file_drop_watcher.py — Bronze Tier Perception Layer

Watches the /Vault/Inbox folder for newly created files.
On detection, stages the file into /Vault/Needs_Action with metadata,
appends to System_Logs.md, and writes a JSONL log entry.
"""

import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WATCH_INTERVAL_MS = int(os.environ.get("WATCH_INTERVAL_MS", "250"))
WATCH_INTERVAL_S = WATCH_INTERVAL_MS / 1000.0

# Dry-run mode: when True, log what WOULD happen without writing any files.
# Defaults to True so the watcher is safe to run in any environment by default.
_dry_run_env = os.environ.get("DRY_RUN", "true").strip().lower()
DRY_RUN = _dry_run_env not in ("false", "0", "no")

IGNORED_SUFFIXES = {".tmp", ".swp", ".ds_store", ".crdownload", ".part"}
IGNORED_NAMES = {".ds_store", "thumbs.db", "desktop.ini"}
IGNORED_PREFIXES = ("~$",)

# Resolve vault root relative to this script's location
VAULT_ROOT = Path(__file__).resolve().parent.parent
INBOX_DIR = VAULT_ROOT / "Vault" / "Inbox"
NEEDS_ACTION_DIR = VAULT_ROOT / "Vault" / "Needs_Action"
LOGS_DIR = VAULT_ROOT / "Vault" / "Logs"
SYSTEM_LOGS_FILE = VAULT_ROOT / "System_Logs.md"

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("file_drop_watcher")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def should_ignore(filepath: Path) -> bool:
    """Return True if the file should be skipped."""
    name_lower = filepath.name.lower()
    if name_lower in IGNORED_NAMES:
        return True
    if filepath.suffix.lower() in IGNORED_SUFFIXES:
        return True
    if any(filepath.name.startswith(p) for p in IGNORED_PREFIXES):
        return True
    return False


def unique_path(target: Path) -> Path:
    """Return a non-colliding path by appending _1, _2, … before the extension."""
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def copy_to_needs_action(original: Path) -> Path:
    """Copy the file into /Vault/Needs_Action with a FILE_ prefix."""
    staged_name = f"FILE_{original.name}"
    target = unique_path(NEEDS_ACTION_DIR / staged_name)
    shutil.copy2(str(original), str(target))
    logger.info("Copied → %s", target.relative_to(VAULT_ROOT))
    return target


def create_task_markdown(original: Path, staged_file: Path) -> Path:
    """Create a YAML-frontmatter task file alongside the staged file."""
    now = datetime.now(timezone.utc).isoformat()
    task_name = f"{staged_file.name}.md"
    task_path = unique_path(NEEDS_ACTION_DIR / task_name)

    relative_artifact = staged_file.relative_to(VAULT_ROOT).as_posix()

    content = f"""---
type: file_drop
source: inbox
original_name: {original.name}
created_at: {now}
status: pending
priority: normal
needs_human_approval: false
related_artifact: {relative_artifact}
---

# New File Dropped

A new file was added to /Vault/Inbox and staged in /Vault/Needs_Action.

## Suggested Actions
- [ ] Review the file
- [ ] Decide next steps
- [ ] (Later) Claude will process and move to /Vault/Done
"""
    task_path.write_text(content, encoding="utf-8")
    logger.info("Task MD → %s", task_path.relative_to(VAULT_ROOT))
    return task_path


def append_system_log(original_name: str, success: bool = True) -> None:
    """Append a human-readable entry to System_Logs.md under Activity Stream."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    status = "SUCCESS" if success else "ERROR"
    entry = (
        f"[{now}] | FILE_DROP_DETECTED | {status} | "
        f"{original_name} staged to Vault/Needs_Action\n"
    )

    text = SYSTEM_LOGS_FILE.read_text(encoding="utf-8")

    marker = "## Activity Stream"
    if marker in text:
        # Replace placeholder line if it's still there
        placeholder = "(Entries will be appended here chronologically.)"
        if placeholder in text:
            text = text.replace(placeholder, entry)
        else:
            # Append after the Activity Stream heading
            idx = text.index(marker) + len(marker)
            text = text[:idx] + "\n" + entry + text[idx:]
    else:
        # Fallback: just append at the end
        text += f"\n{marker}\n{entry}"

    SYSTEM_LOGS_FILE.write_text(text, encoding="utf-8")
    logger.info("System log updated")


def write_jsonl_log(original: Path, staged_file: Path, task_md: Path) -> None:
    """Append a structured JSON log entry to /Vault/Logs/YYYY-MM-DD.jsonl."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{today}.jsonl"

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_type": "file_drop_detected",
        "actor": "file_drop_watcher",
        "source_path": f"Vault/Inbox/{original.name}",
        "staged_file_path": staged_file.relative_to(VAULT_ROOT).as_posix(),
        "task_md_path": task_md.relative_to(VAULT_ROOT).as_posix(),
        "result": "success",
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    logger.info("JSONL log → %s", log_file.relative_to(VAULT_ROOT))


# ---------------------------------------------------------------------------
# Watchdog handler
# ---------------------------------------------------------------------------


class InboxHandler(FileSystemEventHandler):
    """React to new files created in /Vault/Inbox."""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        if should_ignore(filepath):
            logger.debug("Ignored: %s", filepath.name)
            return

        # Brief pause to let the file finish writing
        time.sleep(0.3)

        logger.info("Detected new file: %s", filepath.name)

        if DRY_RUN:
            staged_name = f"FILE_{filepath.name}"
            task_name = f"{staged_name}.md"
            logger.info(
                "[DRY-RUN] Would copy → Vault/Needs_Action/%s", staged_name
            )
            logger.info(
                "[DRY-RUN] Would create task → Vault/Needs_Action/%s", task_name
            )
            logger.info("[DRY-RUN] Would append entry to System_Logs.md")
            logger.info("[DRY-RUN] Would append record to Vault/Logs/YYYY-MM-DD.jsonl")
            logger.info("[DRY-RUN] No files written. Set DRY_RUN=false to enable.")
            return

        try:
            staged = copy_to_needs_action(filepath)
            task_md = create_task_markdown(filepath, staged)
            append_system_log(filepath.name, success=True)
            write_jsonl_log(filepath, staged, task_md)
            logger.info("✓ Processed: %s", filepath.name)
        except Exception:
            logger.exception("Error processing %s", filepath.name)
            try:
                append_system_log(filepath.name, success=False)
            except Exception:
                logger.exception("Failed to write error to System_Logs.md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """Start the watcher."""
    # Ensure directories exist
    for d in (INBOX_DIR, NEEDS_ACTION_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 55)
    logger.info("  File Drop Watcher — Bronze Tier")
    logger.info("  Watching : %s", INBOX_DIR)
    logger.info("  Staging  : %s", NEEDS_ACTION_DIR)
    logger.info("  Logs     : %s", LOGS_DIR)
    logger.info("  Interval : %dms", WATCH_INTERVAL_MS)
    logger.info("  DRY_RUN  : %s", DRY_RUN)
    if DRY_RUN:
        logger.info("  *** DRY-RUN MODE: no files will be written ***")
    logger.info("=" * 55)

    observer = PollingObserver(timeout=WATCH_INTERVAL_S)
    observer.schedule(InboxHandler(), str(INBOX_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down watcher…")
        observer.stop()

    observer.join()
    logger.info("Watcher stopped.")


if __name__ == "__main__":
    main()
