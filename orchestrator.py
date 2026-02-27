"""
orchestrator.py — Silver Tier Orchestrator Framework (Phase 2)

Monitors all active Vault state folders every POLL_INTERVAL_S seconds and
prints a structured status report to stdout.

This phase is OBSERVATION ONLY:
  - No files are moved, created, or modified.
  - No skills are invoked.
  - No Claude calls are made.
  - TODO hooks mark where execution will be wired in future phases.

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

POLL_INTERVAL_S = 5  # seconds between each status scan

VAULT_ROOT = Path(__file__).resolve().parent
NEEDS_ACTION_DIR   = VAULT_ROOT / "Vault" / "Needs_Action"
PLANS_DIR          = VAULT_ROOT / "Vault" / "Plans"
PENDING_APPROVAL_DIR = VAULT_ROOT / "Vault" / "Pending_Approval"
APPROVED_DIR       = VAULT_ROOT / "Vault" / "Approved"
REJECTED_DIR       = VAULT_ROOT / "Vault" / "Rejected"

# Files present in Needs_Action that are NOT actionable task files
NEEDS_ACTION_SKIP = {"README.md", "TRIAGE_SUMMARY.md"}

# Files that are folder metadata, not task or plan content
FOLDER_META = {"README.md"}

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
# State detection helpers
# Each returns a sorted list of Path objects — never modifies or moves files.
# ---------------------------------------------------------------------------


def get_pending_tasks() -> list[Path]:
    """
    Return all pending task .md files in Vault/Needs_Action.

    Excludes:
      - README.md
      - TRIAGE_SUMMARY.md
      - RESULT_*.md  (result documents, not tasks)
      - Non-.md files (staged FILE_* artifacts without extension)
    """
    if not NEEDS_ACTION_DIR.exists():
        return []

    results = []
    for f in sorted(NEEDS_ACTION_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() != ".md":
            continue
        if f.name in NEEDS_ACTION_SKIP:
            continue
        if f.name.startswith("RESULT_"):
            continue
        results.append(f)
    return results


def get_active_plans() -> list[Path]:
    """
    Return all plan files (PLAN_*.md) in Vault/Plans.

    Excludes README.md.
    """
    if not PLANS_DIR.exists():
        return []

    results = []
    for f in sorted(PLANS_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.name in FOLDER_META:
            continue
        if f.suffix.lower() != ".md":
            continue
        results.append(f)
    return results


def get_pending_approvals() -> list[Path]:
    """
    Return all task files waiting for human decision in Vault/Pending_Approval.

    Excludes README.md.
    """
    if not PENDING_APPROVAL_DIR.exists():
        return []

    results = []
    for f in sorted(PENDING_APPROVAL_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.name in FOLDER_META:
            continue
        results.append(f)
    return results


def get_approved_items() -> list[Path]:
    """
    Return all approved task files in Vault/Approved.

    Excludes README.md.
    These are tasks cleared by a human and ready for orchestrator re-queuing.
    """
    if not APPROVED_DIR.exists():
        return []

    results = []
    for f in sorted(APPROVED_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.name in FOLDER_META:
            continue
        results.append(f)
    return results


def get_rejected_items() -> list[Path]:
    """
    Return all rejected task files in Vault/Rejected.

    Excludes README.md.
    These are tasks a human declined — no further action is taken on them.
    """
    if not REJECTED_DIR.exists():
        return []

    results = []
    for f in sorted(REJECTED_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.name in FOLDER_META:
            continue
        results.append(f)
    return results


# ---------------------------------------------------------------------------
# Status printer
# ---------------------------------------------------------------------------


def print_status(
    pending: list[Path],
    plans: list[Path],
    approvals: list[Path],
    approved: list[Path],
    rejected: list[Path],
) -> None:
    """Print a structured status block to stdout via the logger."""
    sep = "-" * 40
    logger.info(sep)
    logger.info("[ORCHESTRATOR STATUS]")
    logger.info("Pending Tasks    : %d", len(pending))
    logger.info("Active Plans     : %d", len(plans))
    logger.info("Waiting Approval : %d", len(approvals))
    logger.info("Approved         : %d", len(approved))
    logger.info("Rejected         : %d", len(rejected))
    logger.info(sep)

    if pending:
        logger.info("  Pending tasks:")
        for f in pending:
            logger.info("    → %s", f.name)

    if plans:
        logger.info("  Active plans:")
        for f in plans:
            logger.info("    → %s", f.name)

    if approvals:
        logger.info("  Waiting approval:")
        for f in approvals:
            logger.info("    → %s", f.name)

    if approved:
        logger.info("  Approved (awaiting re-queue):")
        for f in approved:
            logger.info("    → %s", f.name)

    if rejected:
        logger.info("  Rejected:")
        for f in rejected:
            logger.info("    → %s", f.name)


# ---------------------------------------------------------------------------
# Future execution hooks (placeholders — no logic implemented yet)
# ---------------------------------------------------------------------------


def _hook_create_plan(pending: list[Path]) -> None:
    # TODO: create_plan hook
    # For each pending task that lacks a corresponding PLAN_*.md in Vault/Plans,
    # invoke the plan-writing skill to generate a structured execution plan.
    # This will call Claude via subprocess or SDK in a future phase.
    # Input:  list of pending task Path objects
    # Output: writes PLAN_<task>.md to Vault/Plans/
    pass


def _hook_execute_plan(plans: list[Path]) -> None:
    # TODO: execute_plan hook
    # For each plan file in Vault/Plans whose corresponding task does NOT
    # require human approval, invoke the close_task skill to process it.
    # This will call Claude via subprocess or SDK in a future phase.
    # Input:  list of active plan Path objects
    # Output: moves task + result to Vault/Done/, appends logs
    pass


def _hook_approval_processing(approved: list[Path]) -> None:
    # TODO: approval_processing hook
    # For each file in Vault/Approved, re-queue the task into Vault/Needs_Action
    # with needs_human_approval set to false, then remove it from Vault/Approved.
    # This enables the normal close_task flow to pick it up on the next cycle.
    # Input:  list of approved item Path objects
    # Output: copies/moves task back to Vault/Needs_Action with updated frontmatter
    pass


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


def run() -> None:
    """Start the orchestrator polling loop."""
    logger.info("=" * 55)
    logger.info("  Orchestrator — Silver Tier (Phase 2)")
    logger.info("  Vault root : %s", VAULT_ROOT)
    logger.info("  Interval   : %ds", POLL_INTERVAL_S)
    logger.info("  Mode       : OBSERVE ONLY (no execution)")
    logger.info("  NOTE       : Claude invocation NOT active yet")
    logger.info("=" * 55)

    while True:
        # --- Collect state -------------------------------------------------
        pending   = get_pending_tasks()
        plans     = get_active_plans()
        approvals = get_pending_approvals()
        approved  = get_approved_items()
        rejected  = get_rejected_items()

        # --- Report state --------------------------------------------------
        print_status(pending, plans, approvals, approved, rejected)

        # --- Future execution hooks (placeholders) -------------------------
        _hook_create_plan(pending)       # TODO: create_plan hook
        _hook_execute_plan(plans)        # TODO: execute_plan hook
        _hook_approval_processing(approved)  # TODO: approval_processing hook

        # --- Wait for next cycle -------------------------------------------
        time.sleep(POLL_INTERVAL_S)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Orchestrator shutting down cleanly.")
        logger.info("No files were modified during this session.")
        sys.exit(0)
