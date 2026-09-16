> AI code review — automated review for reference; please use your judgment.

Textbook refactor: the extracted helper is genuinely more capable than the inline block it replaced (idempotent + revocable via strip-then-apply, preserving unrelated betas/extra_body keys through the revoke, never mutating the caller's dict) while remaining byte-identical on the enabled path — and the single test asserts all five of those properties explicitly, including end-to-end delegation through `build_anthropic_kwargs`. The docstring's strip-before-decide rationale is exactly what makes the revocable semantics trustworthy.

— reviewer-b (automated review)

No blocking issues found.
