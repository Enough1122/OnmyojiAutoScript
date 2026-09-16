> AI code review — automated review for reference; please use your judgment.

Straightforward catalog addition, and the OAuth-fallback rationale in the new test is a nice touch. Minor items:

- agent/usage_pricing.py:216 — issue — the `claude-opus-5-fast` entry declares `source="official_docs_snapshot"` but its `source_url` is openrouter.ai, unlike the two base entries that cite platform.claude.com — why it matters — provenance fields exist so future audits can tell verified-official from aggregator-derived numbers; a mislabeled source silently erodes that — suggestion — either point `source_url` at the official pricing page (if it documents the fast lane) or set `source="openrouter"` to match reality.

- agent/usage_pricing.py:222 — issue — the base model gets a dated-snapshot alias (`claude-opus-5-20260723`) but the fast variant does not (`claude-opus-5-fast-20260723` absent) — why it matters — if the Anthropic API echoes dated IDs for the fast lane the way it does for base Opus, those responses will miss the exact-match pricing entry and fall back to whatever estimate path exists — suggestion — confirm how cost lookup normalizes dated suffixes and add the dated fast alias (or a documented normalization) so both lanes behave identically.

- tests/hermes_cli/test_anthropic_picker_curated.py:36 — issue (coverage) — the new test only exercises the picker side; nothing asserts the three new model IDs actually resolve in `usage_pricing`'s table — why it matters — these two catalogs have drifted apart before (that's the failure mode the curated-list docstring itself describes); a missing pricing entry surfaces later as wrong cost reporting — suggestion — add a small parametrized test asserting each curated Anthropic ID (at minimum the three added here) has a `PricingEntry` with positive input/output costs.

No blocking issues found — all three items are consistency/hygiene rather than functional regressions.

— reviewer-b (automated review)
