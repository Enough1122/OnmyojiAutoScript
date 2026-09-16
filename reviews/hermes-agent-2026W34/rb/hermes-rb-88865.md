> AI code review — automated review for reference; please use your judgment.

Correct fix with the ordering insight stated plainly: the client-surface fold runs *after* platform resolution, so `agent.disabled_toolsets` has to be re-subtracted after it or GUI surfaces resurrect disabled toolsets. Applying it at both return sites, parsing the JSON-array-string spelling `hermes config set` produces, and leaving the operator env-pin supreme are all the right calls, each pinned by a test. Items:

- tui_gateway/server.py:4484 — nit — `_disabled_agent_toolsets()` swallows every exception into an empty set (fail-*open*: a transient config-read error silently re-enables disabled toolsets for that resolution) and is invoked on every `_load_enabled_toolsets` call — suggestion — add a `logger.debug/warning` on the error path so a misconfigured `disabled_toolsets` value is diagnosable, and rely on `load_config`'s own cache for the repeat-call cost.

No blocking issues found.

— reviewer-b (automated review)
