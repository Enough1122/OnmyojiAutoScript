> AI code review — automated review for reference; please use your judgment.

Correct fix with the concurrency subtleties handled: runtime resolution moved *inside* the executor closure so the ContextVar-carrying helper keeps profile scoping while blocking work stays off the event loop, and `main_runtime` is threaded through all three layers so the judge's `auto` aux resolution follows mid-session preset swaps. The test asserts both off-loop thread affinity and exact forwarded kwargs. Items:

- hermes_cli/goals.py:1299 — issue (verification) — `draft_contract` gains the `main_runtime` parameter, but no visible caller threads it (the gateway's contract-drafting path isn't in the diff) — why it matters — if contracts are drafted against the stale global route while judging follows the live one, the contract's model assumptions and the verdict can come from different providers mid-session — suggestion — either thread `main_runtime` at the draft call sites too, or note why drafting is exempt.

- gateway/run.py:21310 — nit — session-runtime resolution failure is logged at debug only, then `main_runtime=None` silently reverts the judge to the process-global route; a single `logger.info` would make post-preset-swap regressions of this exact class diagnosable from logs.

No blocking issues found.

— reviewer-b (automated review)
