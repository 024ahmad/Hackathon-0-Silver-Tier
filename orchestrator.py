"""
orchestrator.py — Bronze Tier Orchestrator Stub

Polls Vault/Needs_Action for pending task files and reports their count.
Does NOT invoke Claude or process tasks automatically — that is reserved for
Silver tier when a full reasoning loop will be added.

Usage:
    python orchestrator.py

Stop with Ctrl+C.
"""

import logging
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLL_INTERVAL_S = 5  # seconds between each scan

VAULT_ROOT = Path(__file__).resolve().parent
NEEDS_ACTION_DIR = VAULT_ROOT / "Vault" / "Needs_Action"

# Files that are present in Needs_Action but are NOT pending tasks
NON_TASK_FILES = {"README.md", "TRIAGE_SUMMARY.md"}

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("orchestrator")

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def count_pending_tasks() -> list[Path]:
    """Return a list of pending task .md files in Vault/Needs_Action."""
    if not NEEDS_ACTION_DIR.exists():
        return []

    pending = []
    for f in sorted(NEEDS_ACTION_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() != ".md":
            continue
        if f.name in NON_TASK_FILES:
            continue
        if f.name.startswith("RESULT_"):
            continue
        pending.append(f)
    return pending


def run():
    """Main polling loop."""
    logger.info("=" * 55)
    logger.info("  Orchestrator Stub — Bronze Tier")
    logger.info("  Watching : %s", NEEDS_ACTION_DIR)
    logger.info("  Interval : %ds (poll only — no auto-processing)", POLL_INTERVAL_S)
    logger.info("  NOTE     : Claude invocation NOT implemented yet")
    logger.info("=" * 55)

    while True:
        pending = count_pending_tasks()
        count = len(pending)

        if count == 0:
            logger.info("Queue empty — no pending tasks in Vault/Needs_Action")
        else:
            logger.info("Pending tasks: %d", count)
            for task in pending:
                logger.info("  → %s", task.name)

        time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        logger.info("Orchestrator stopped.")
