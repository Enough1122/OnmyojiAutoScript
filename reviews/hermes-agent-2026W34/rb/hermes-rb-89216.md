> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Useful roster enrichment with full-stack plumbing: the backend summaries now carry `model`/`input_tokens`/`output_tokens` through both the pinned and latest-session projections (including the compression-tip fallback, tested), and the row renders a truncated model plus a compact token label with a dedicated formatter under unit-boundary tests. Findings:

1. apps/desktop/src/plugins/hermes-bots/tests/roster-preview.test.mjs:93 — the assertion `format(999_500) === '1.0M tokens'` **contradicts the implementation**: 999_500 divides once to `scaled = 999.5` (`unitIndex = 1`, 'k'), which is below the continuation threshold, so the function returns `"999.5k tokens"`. Either the test fails today or it documents an intent the code doesn't have (round *up* to the next unit when within rounding distance of the boundary). Decide the contract — plain `999.5k`, or a ceil-to-`1.0M` rule implemented explicitly (`if (rounded >= 1000 - epsilon) bump unit`) — and make code and test agree before merge; right now one of them is wrong and CI presumably proves which.

2. Nit: summing `input_tokens + output_tokens` hides cache economics now that `cache_read` exists (#89772); fine for a glanceable label, but consider labeling it "total" in the tooltip since power users will read it as billed tokens.
