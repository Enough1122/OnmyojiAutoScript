> AI code review — automated review for reference; please use your judgment.

The staged two-`os.replace` swap, fsync'd atomic lock writes, and commit-marker recovery are all the right machinery, and the "preserve the previously active skill as the primary invariant" ordering in the lock-failure rollback is correctly prioritized. One real gap and two smaller points:

- tools/skills_hub.py:4089 — issue — if the *second* `os.replace(staging_dir, install_dir)` fails, control jumps to the **outer** `except`, which returns staging to quarantine and re-raises — but the active skill has already been moved to `backup_dir` and is never restored in this call — why it matters — between this failed install and whenever the next install runs its recovery preamble, the skill directory simply does not exist: loaders see a missing skill with no event explaining it — suggestion — in the outer handler, when `had_previous and backup_dir.exists() and not install_dir.exists()`, do `os.replace(backup_dir, install_dir)` before returning staging to quarantine (mirroring the inner rollback).

- tests/tools/test_skills_hub.py:1658 — issue (coverage) — none of the three interrupted-recovery branches introduced here are directly tested (backup-without-target → restore; backup+matching-hash → cleanup-only; backup+mismatched-hash → rollback); they encode subtle decisions against the lock hash that future refactors will get wrong — suggestion — three small fixtures that pre-create `backup_dir`/`install_dir` states and assert each branch's outcome.

- tools/skills_hub.py:4060 — nit — the function now carries four distinct recovery paths across nested handlers; extracting the swap into `_swap_staged_install(...)` with an explicit result enum would make the invariants testable in isolation instead of through full-install fixtures.

No blocking issues found — item 1 closes a real availability hole in exactly the scenario ("update goes wrong") this PR exists to fix.

— reviewer-b (automated review)
