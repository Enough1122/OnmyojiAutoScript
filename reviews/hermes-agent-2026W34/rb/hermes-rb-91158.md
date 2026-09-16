> AI code review — automated review for reference; please use your judgment.

1. `agent/conversation_compression.py:~2455–2462` (`compress_context`) — the attributed suffix ````COMPACTION_STATUS + compaction_reason_clause(...)```` appears to be **overwritten two lines later** on the `not force` path (````_compaction_status = automatic_compaction_status_message(...)````, which takes no trigger argument) — why it matters: that makes the *automatic* arms (threshold/pre_api_pressure/overflow_*/post_tool_threshold — most of the vocabulary!) lose their user-facing clause while manual paths keep theirs, i.e. inverted from the stated goal; the new e2e auto test asserts the clause IS present, so either the surrounding guards make this unreachable for real fires or the test exercises a path where the overwrite doesn't happen — suggestion: please confirm which it is, and if the overwrite is live, thread the clause into `automatic_compaction_status_message` (or re-append after it).

2. `tests/agent/test_compaction_trigger_coverage.py:~20–27` (`_PRODUCER_GLOBS`) — the producer scan uses **non-recursive** globs (````"agent/*.py"````, ````"gateway/*.py"````), so any future call site placed in a subpackage (`agent/monitoring/*.py` already exists) escapes attribution coverage entirely while feeling protected — suggestion: switch to recursive patterns (````"agent/**/*.py"```` etc., plus ````"tui_gateway/**/*.py"````); the scan-finds-producers guard should also assert one subdirectory file so this can't regress silently.

3. Nit (`:~30–31`): `_LITERAL_RE` matches only lowercase snake_case literals; a future `trigger_reason="Overflow413"` variant would slip the scan — fine given the convention, worth one comment line stating the naming constraint is load-bearing.

Otherwise excellent: the never-silent fallback for unknown reasons, the raw-label-vs-prose distinction in tests, the guarded-guard meta-test, suffix placement explicitly justified against the gateway noise filters, and every call site across CLI/TUI/gateway/ACP updated in lockstep with updated fakes. Item 1 just needs a definitive answer before merge.

— reviewer-a · automated agent review (Hermes week-review)
