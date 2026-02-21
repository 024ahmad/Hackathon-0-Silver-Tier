ROLE:
You are a senior software architect refactoring a local-first AI Employee project into a cleaner, more professional structure. 
Your job is to introduce a proper "Vault" directory and migrate all state-related folders into it, while keeping the system fully functional.

You must:
- Work carefully and safely.
- Preserve all data.
- Not delete any files.
- Update all references and paths accordingly.
- Keep the project runnable after refactor.
- Be idempotent (do not break if re-run).

CONTEXT:
Current project structure includes these folders at root:
- Inbox/
- Needs_Action/
- Done/
- Logs/
- Skills/
- Watchers/

Goal:
Introduce this structure:

/Vault
   /Inbox
   /Needs_Action
   /Done
   /Logs

And keep:
/Skills
/Watchers
pyproject.toml
README.md
etc.
at root level.

---------------------------------------------------
TASKS
---------------------------------------------------

1️⃣ Create a new folder at project root:
   ./Vault

2️⃣ Move the following folders INTO Vault:
   - Inbox
   - Needs_Action
   - Done
   - Logs

   Final structure must be:
   Vault/Inbox
   Vault/Needs_Action
   Vault/Done
   Vault/Logs

3️⃣ Do NOT move:
   - Skills/
   - Watchers/
   - .venv
   - pyproject.toml
   - README.md
   - Dashboard.md
   - Company_Handbook.md
   - System_Logs.md
   - Bronze_Runbook.md
   - Bronze_Proof_Pack.md

4️⃣ Update ALL hardcoded paths in:
   - Watchers/*.py
   - Skills/*.md
   - Bronze_Runbook.md
   - Bronze_Proof_Pack.md
   - main.py (if exists)

   Replace:
      ./Inbox → ./Vault/Inbox
      ./Needs_Action → ./Vault/Needs_Action
      ./Done → ./Vault/Done
      ./Logs → ./Vault/Logs

   Use relative paths consistently via pathlib.
   Do not introduce absolute paths.

5️⃣ Update watcher scripts so they:
   - Watch /Vault/Inbox
   - Stage files to /Vault/Needs_Action
   - Log to /Vault/Logs
   - Update System_Logs.md at root

6️⃣ Verify that:
   - Watcher still runs without error.
   - No broken imports.
   - No path conflicts.
   - All logging still works.

7️⃣ After refactor:
   - Print a tree view (2 levels deep).
   - Show example of updated watcher path usage.
   - Confirm system is ready.

---------------------------------------------------
QUALITY RULES
---------------------------------------------------
- Use pathlib in Python.
- Avoid string-based path concatenation.
- Preserve file timestamps where possible.
- Do not reformat unrelated files.
- Keep commit-style clarity in changes.

---------------------------------------------------
OUTPUT
---------------------------------------------------
Return:
- Summary of what was moved
- Summary of what files were updated
- Final tree structure
- Confirmation: "Vault refactor complete and system operational."