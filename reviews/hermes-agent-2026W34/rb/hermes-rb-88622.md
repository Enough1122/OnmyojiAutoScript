> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct reclassification: `/context` is a read-only parent-session command, so routing it through the agent-less slash worker both spawned an unnecessary process and failed on resumed sessions whose transcript exists without a resident agent. Normalizing aliases through `resolve_command` before the direct-command set lookup also fixes `/ctx` for free, and the parametrized test pins both spellings while asserting *no* worker spawn via an exploding `_SlashWorker`. Moving the concurrency race test off `/context` was the right follow-through since it no longer takes that path. Findings below are minor:

1. tui_gateway/server.py:_live_slash_command_output — the `resolve_command` probe is wrapped in a bare `except Exception: pass`; if the commands module ever fails to import or changes its API, alias normalization silently stops working and users see "unknown command" for `/ctx` again with zero diagnostics. A `logger.debug` on the except branch keeps the degrade graceful but visible.
