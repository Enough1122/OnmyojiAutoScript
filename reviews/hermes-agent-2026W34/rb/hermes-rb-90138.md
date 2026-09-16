> AI code review — automated review for reference; please use your judgment.

Right fix: a dry-run tester that says "would prompt" while the runtime would actually allow is exactly the kind of drift that makes the tool untrustworthy, and the new `is_approved(session_key, pattern_key)` check reuses the runtime's own predicate instead of duplicating its logic. The test matrix is the highlight: permanent, session, *other-session* (must NOT allow), hardline-beats-class-key, and user-deny-beats-class-key — precedence both directions pinned. Points:

1. hermes_cli/approvals_test.py:~136 — the inserted check sits inside the dangerous-pattern branch, i.e. *after* whatever earlier steps handle yolo/permanent-allowlist/user-deny/hardline. That implicitly encodes a precedence order; one comment naming the intended full ordering ("hardline > user-deny > session > permanent > prompt") at the top of the function would keep future steps from being inserted in an order that silently changes semantics.
2. The fixture now saves/restores `_session_approved` alongside `_permanent_approved` — good catch; partial state leakage between tests would have made the other-session case flaky. (positive)
3. Detail-string nit: "already approved for this session or in command_allowlist" — if `_permanent_approved` also feeds `is_approved`, the message should mention permanent approvals too, since that's arguably the most common source. (nit)
4. No test for yolo-enabled + class-key (yolo presumably short-circuits earlier — one assertion would pin that assumption). (nit)

No blocking issues found.
