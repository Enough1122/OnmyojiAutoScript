> AI code review — automated review for reference; please use your judgment.

Small, correct, and exactly scoped: surfacing the provider's error body (bounded via the existing `_truncate`, so the continuation prompt can't balloon) turns an undiagnosable "PermissionDeniedError" into an actionable reason while preserving fail-open semantics — and the tests cover all three properties including the length bound. One nit:

1. hermes_cli/goals.py:~1258 — SDK exceptions sometimes carry an empty `str(exc)` (message lives only on `exc.body`/`exc.status`), producing a dangling `"judge error: PermissionDeniedError: "`. Falling back to \`getattr(exc, "status", "") or type name\` when the body is empty would keep the reason informative for that class too. (nit)

No blocking issues found.
