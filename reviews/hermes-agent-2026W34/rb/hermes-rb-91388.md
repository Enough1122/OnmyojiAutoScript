> AI code review — automated review for reference; please use your judgment.

1. hermes_cli/model_switch.py:2145 — the predicate swap deliberately broadens coverage beyond the two named cases: *every* provider name `opencode_provider_family` accepts now routes through `opencode_model_api_mode`. Why it matters: if that function has no safe default for an accepted family slug whose model is missing from its routing table, a previously-working custom chat_completions provider regresses to a wrong wire or an error. Suggestion: add a test for an accepted family name paired with an unlisted model, asserting it degrades gracefully to the generic default rather than raising.

2. tests/hermes_cli/test_model_switch_opencode_anthropic.py:175 — the two new cases cover `opencode-free` and a custom go-family bridge, but nothing pins the original built-ins (`opencode`, `opencode-zen`, `opencode-go`) to their existing modes. Why it matters: if the family matcher's definition ever shifts, this PR's own regression suite wouldn't notice a narrowing back toward the old bug. Suggestion: parametrize one assertion over the three original slugs.

3. hermes_cli/model_switch.py:2138 — nit: the inline comment reproduces the test class docstring almost verbatim, including the fragile "30 lines below" cross-reference that will rot on the next edit. Keep the full rationale next to the tests and leave a one-line pointer (plus the #85589 reference) here.

4. hermes_cli/model_switch.py:2146 — suggestion: emit a debug log when this override fires (`provider`, resolved family, chosen `api_mode`). Misrouting reports currently give no trace of which branch decided the wire mode, and this branch just became the sole decider for a wider provider set.
