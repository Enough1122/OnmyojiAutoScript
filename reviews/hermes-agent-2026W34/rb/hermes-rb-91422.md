> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct and well-scoped fix: `agent.disabled_toolsets` is a denial policy, so the api_server agent build ignoring it meant deployments that removed e.g. delegation for safety reasons were silently re-enabled on this surface. Passing it through mirrors the messaging-platform build, the None case preserves prior behavior, and both paths are pinned by tests (including the list-shaped config form).

Nit (non-blocking): gateway/platforms/api_server.py:2937 — if the configured value is a malformed type that `parse_config_string_list` can't interpret, it degrades to `None`, which for a *safety* denial is the fail-open direction: an operator typo (e.g. a nested mapping instead of a list) re-enables the toolset with no signal. Consider logging a warning whenever the raw value is non-empty but parses to empty/None, so misconfiguration is visible in gateway logs rather than discovered by an unexpectedly available tool.
