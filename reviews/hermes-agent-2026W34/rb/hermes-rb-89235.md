> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-contained enhancement: the sibling extraction is deliberately best-effort (unresolvable ids never fail the worker's exit path), the link insert is cycle-checked and idempotent inside the caller's transaction, and every outcome — resolved/link-created, unresolved, cycle-error — lands on the `dependency_wait` event payload for alerting. The three tests prove the part that matters most end-to-end: the persisted parent link actually gates `recompute_ready` until the named sibling completes, which is exactly the re-promotion bug this targets. Findings below are minor:

1. hermes_cli/kanban_db.py:_resolve_dependency_sibling — only the **first** resolvable sibling is linked, so a reason like "waiting on {X} and {Y}" parks the card behind X alone; once X completes, `recompute_ready` promotes the card even though Y is still open — recreating a milder version of the premature-promotion bug for multi-dependency blocks. Since the regex already finds all candidates, consider linking *every* resolvable one (recording per-candidate outcomes in the event payload) rather than stopping at the first.
