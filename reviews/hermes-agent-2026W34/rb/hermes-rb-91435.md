> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right call for #88521: token locks are machine-global, so a sibling profile holding the same bot token is a *config conflict*, not a stale slot — SIGTERM'ing it under a supervisor that auto-restarts every profile with `--replace` just manufactures a flap loop (with cron children reaped as collateral). The same-home takeover path survives intact, the guard sits after identity validation, and the new tests cover both branches including the adapter-level retryable-conflict surface with the actionable "'personal' profile gateway" wording. Findings:

1. gateway/status.py:2076 — this deliberately deletes a previously *designed* capability: the old contract explicitly supported an explicit cross-profile `--replace` via planned-takeover markers written into the target's home (marker consumption existed precisely to prevent supervisor revival loops). After this PR there is no way to remotely replace a gateway running under a different HERMES_HOME — operators migrating a bot token between profiles must manually stop the sibling first. If that's intended, say so loudly: update the gateway docs/upgrade notes ("cross-profile replace requires stopping the other profile") and ideally have the conflict message link to them; if not, consider an opt-in flag (e.g. `--replace-any-home`) reserved for human-invoked runs, never the s6 default.

2. gateway/platforms/base.py:3530 — the docstring now says a live different-home holder makes the lock "stay retryable", which is correct, but the reconnect watcher will keep retrying indefinitely against a conflict only a human can resolve; consider escalating to a distinct fatal error code after N consecutive conflicts so dashboards can distinguish "waiting for sibling to die" from a flapping token.

3. tests/gateway/test_status.py:910 — nit: `_arm_live_owner` primes three alive-polls (`[True, True, False]`) but the distinct-home test returns before any poll happens; trim to what each test consumes so future readers don't infer polling semantics that aren't exercised.
