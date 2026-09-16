> AI code review — automated review; please use your judgment.

Small, well-tested feature: both wrap modes queue `_pending_agent_seed` exactly like existing seed-based commands, aliases are registered (`fw`/`quick-wrap`, `daily-wrap`/`wrap-full`), `cli_only=True` keeps them out of gateway surfaces, and the test coverage goes beyond the happy path — alias resolution, the cli_only contract, and notably the slash-completer disambiguation test for "/fa" now that "/fast-wrap" exists alongside "/fast".

No blocking issues found.

Nits:
1. Neither command checks that the session-wrap skill it references is actually installed; on a bare install the seed silently steers toward a nonexistent skill. A one-line availability note in the queued message (or a warning when the skill is missing) would close that gap.
2. The website slash-command reference isn't touched — if there's a user-facing command list, these two belong in it.

— reviewer-a · automated agent review (Hermes week-review)
