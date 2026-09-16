> AI code review — automated review for reference; please use your judgment.

Good fix plus a guard that outlives it: the translations are proper French (typography included — espace before `%` and colon) and the new test encodes the real failure mode ("key parity proves existence, not translation") with the placeholder-only `bar` key correctly exempted. One forward-looking nit:

- tests/agent/test_i18n.py:78 — nit — the copy-through guard is scoped to `fr` × `gateway.context.`; the same silent-copy failure can hit any locale/block — consider generalizing to "every non-en locale, every key" (with a small known-English allowlist) once other blocks are confirmed translated.

No blocking issues found.

— reviewer-b (automated review)
