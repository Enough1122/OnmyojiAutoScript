> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Textbook behavior-neutral refactor: `run_conversation` is now a thin owner of one finalization scope (token-set ContextVar → impl → observe → reset, with `complete` deliberately running *before* `reset` so the terminal reason is still readable), every one of the ~20 exit-reason assignments routes through `_record_turn_exit_reason` while returning the identical local value, and the observer only emits a redacted breadcrumb — it cannot replace a result or mask an exception, and the redaction itself fails closed to `[REDACTED]`. The parity test matrix (normal/partial/interrupted/budget/error × totals-unchanged × finalize-once) plus a barrier-synchronized concurrency test is precisely the safety net this kind of unification needs. Findings:

1. agent/conversation_loop.py:94 — the module now imports four private helpers (`_begin_turn_finalization`, `_complete_turn_finalization`, `_record_turn_exit_reason`, `_reset_turn_finalization`) across module boundaries. They're load-bearing public API of the finalizer contract now; rename without underscores (or expose an explicit small facade) so a future cleanup doesn't treat them as removable internals and break the wrapper silently. Purely naming/API hygiene — behavior is right.
