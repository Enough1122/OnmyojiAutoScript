> AI code review — automated review for reference; please use your judgment.

The webhook profile-scoping fix (#88409) itself is well done — every read/write/restart path routed through `_config_profile_scope`, with tests proving both isolation directions and that created subscriptions land where the gateway actually reads. But two concerns:

- PR composition — issue — this PR bundles **four unrelated changes** behind a webhook-scoping title: (a) webhook profile scoping, (b) a new 2-minute 402 TTL + `is_billing` redefinition in `credential_pool.py`, (c) multi-dir deduped skill counting in `profiles.py`, (d) `clear_session_cache()` on context-engine transitions in `run_agent.py` — why it matters — each carries independent risk (especially b, which changes failover behavior), and bisecting a future regression across all four will be painful — suggestion — split into focused PRs, or at minimum enumerate all four changes explicitly in the description.

- agent/credential_pool.py:363 — issue (behavior confirmation) — moving the 402 early-return *before* the `is_billing` computation means a credential whose failure was *classified* as billing exhaustion (not just a raw 402) now also benches only 2 minutes instead of an hour when error_code happens to be 402 — why it matters — for genuinely month-end-exhausted accounts this converts one long bench into a 2-minute retry loop issuing a request every cycle — suggestion — confirm the extra request cadence is acceptable for hard-depleted accounts, or restrict the short TTL to unclassified/402-self-evident cases.

No blocking issues found beyond the bundling hygiene.

— reviewer-b (automated review)
