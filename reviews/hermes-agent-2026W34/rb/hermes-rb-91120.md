> AI code review — automated review for reference; please use your judgment.

Correct fix with unusually convincing evidence: `optimize` merges segments but leaves deleted rows in the `*_data` shadow tables, so only `rebuild` lets VACUUM actually return tombstone pages — and the 1.7 GB → 86 MB measurement makes the case unarguable. The trace-callback test asserting a `'rebuild'` statement fires *and no* `'optimize'` does is exactly how to pin this.

- hermes_state.py:12814 — issue (verification) — `vacuum()`'s return value changed meaning from "indexes merged" to "indexes rebuilt"; please confirm every consumer was updated — the auto-maintenance bookkeeping (`maybe_auto_prune_and_vacuum` / whatever records successful vacuums) and any remaining user-facing string saying "merged" — why it matters — a stale count label is cosmetic, but an auto-maintenance path keying decisions off the old semantics would silently misreport health.

- hermes_state.py:12830 — issue (UX/runtime) — `rebuild_fts` re-reads every message and recreates the trigram index; on the very GB-scale DBs this targets that's a minutes-long operation inside a window that also wants an exclusive lock, and if the auto-prune path triggers it at startup users experience an unexplained hang with zero feedback — why it matters — perceived freeze → force-quit mid-VACUUM is worse than the original bloat — suggestion — log start/duration and row counts around the rebuild (`logger.info("FTS rebuild: %d messages…")`), and consider having the automatic path use rebuild only when the preceding prune deleted a meaningful number of sessions, keeping manual `hermes sessions optimize` as the unconditional entry point.

- tests/test_hermes_state.py:2603 — nit — the spy replaces the bound method on the instance, so a future refactor that calls `HermesState.rebuild_fts(self)` via the class would bypass the spy while the trace-callback assertions still catch it — fine as defense in depth, just noting the primary signal is the SQL trace, not the spy.

No blocking issues found — item 2 is worth doing before this ships to auto-maintenance.

— reviewer-b (automated review)
