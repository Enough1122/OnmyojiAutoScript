> AI code review — automated review for reference; please use your judgment.

Correct diagnosis (provider IDs are correlation aliases, not identity) and the right cure: position-indexed resolution with an explicit refuse-to-guess rule for genuinely ambiguous cases. The extraction into `agent/tool_occurrences.py` keeps both compression sites consistent, and the redaction parity on the summary path is preserved. Items:

- agent/tool_occurrences.py:88 — issue — when a result is ambiguous (`len(candidates) != 1`) it is silently left unmapped, and every downstream demotion then labels it `[unknown]`; nothing logs or counts these events — why it matters — a provider that reuses IDs concurrently will degrade compression quality (wrong names in summaries/prunes) invisibly; the strictness is right, the silence isn't — suggestion — increment a module-level counter / emit one `logger.debug` per unresolved result including its refs, so a quality dip in compaction output can be traced back to ID ambiguity in minutes rather than archaeology.

- agent/tool_occurrences.py:44 — issue (documentation) — the composite convention (`call_abc|fc_123`, stable-provider-ID first) is implied by `_normalize_ref` splitting on the *first* pipe and by one test fixture, but nowhere stated — why it matters — any producer that emits `fc_123|call_abc` still works here (both segments become aliases only via raw/no-pipe rule… actually it doesn't: a leading-segment swap changes which alias is primary), so cross-component drift is possible — suggestion — document the canonical layout in the module docstring and add a swapped-order fixture asserting current behavior explicitly.

- tests/agent/test_tool_occurrences.py:24 — issue (coverage) — missing two realistic shapes: (a) the trivial single call+result pair (the most common case in real transcripts!), and (b) three parallel calls in one assistant message with *distinct* IDs whose results arrive in swapped order — why it matters — (b) is exactly the candidate-set logic this module exists for under mild stress; today only the degenerate duplicate case exercises multi-candidate handling — suggestion — add both; each is a five-line fixture.

No blocking issues found — the design is sound; items 1–3 harden it.

— reviewer-b (automated review)
