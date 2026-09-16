> AI code review — automated review for reference; please use your judgment.

Correct ownership semantics: the per-tick overlay `{**default, **own}` shadows only the platforms a profile actually runs (its Discord cron output goes out via *its* bot) while everything else falls back to the default map — and the overlay builds a fresh dict, so the shared default map provably never mutates (the test asserts identity, not just values, which is exactly the right assertion here). Reading the gateway's live `profile_adapters` dict per tick rather than snapshotting at start() means secondary profiles that connect after boot are included without any restart, and the comment says so explicitly.

No blocking issues found.

Nit: the headline design property — "late-connecting profile adapters are picked up because the dict is read per tick" — is asserted in prose but not in tests: every current case passes a static map. One test that starts the scheduler, then injects a new key into `profile_adapters` before the second tick and asserts the next tick's overlay includes it, would pin the exact behavior a future "cache the map for efficiency" refactor would silently break. Cheap to add against the existing tracking-tick harness.

— Reviewed by Hermes AI reviewer (reviewer-f2)
