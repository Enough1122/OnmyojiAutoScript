> AI code review — automated review for reference; please use your judgment.

Excellent hardening of exactly the right seam: implicit DEFERRED→write-lock upgrade was producing mid-batch SQLITE_BUSY under cross-process contention, and the shared `state_db_begin_immediate` primitive gives both helper writers SessionDB's discipline without dragging SessionDB-only machinery along. The design decisions are all documented where they'll be read: body-not-retried (side-effect safety), message-scoped retry predicate (SQLite class hierarchy varies by build), connection lifecycle left with the helpers (fd-leak contract preserved), constants mirrored to avoid convoy sync. Real-contention tests drive actual competing `BEGIN IMMEDIATE` holders through both helpers. Items:

- hermes_state_common.py:845 — nit — the contract documents BEGIN-failure and body-exception paths but not a failing `COMMIT` (rare WAL edge: disk I/O / checkpoint interference); today it propagates after no rollback attempt, which is fine — one sentence stating "COMMIT failures propagate unrolled-back-by-design" closes the contract.

- hermes_cli/profiles.py — nit (observation, not this PR's code) — the docstring notes `_DB_LOCK` stays put; worth adding that the primitive's win is therefore *cross-process* only, so nobody later "simplifies" by removing the in-process locks believing this covers them.

No blocking issues found.

— reviewer-b (automated review)
