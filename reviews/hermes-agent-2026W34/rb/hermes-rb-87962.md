> AI code review — automated review for reference; please use your judgment.

Review of "fix(vision): keep tools available for named custom providers". Correct fix for a multi-profile availability bug: a transient profile-backed lookup failure used to strip vision tools from the whole turn (and silently, with no signal). The two-layer remedy is right — contain the lookup exception, then recover through the live main runtime ONLY when the requested-provider identity matches (`_custom_identity` normalization, explicit rejection of unrelated runtimes tested so nothing borrows another session's endpoint), and capability-probe failures now log WHY instead of silently disabling tools. Suggestions:

1. agent/auxiliary_client.py:_custom_identity (nit) — `removeprefix("custom:")` normalizes one prefix but not case variants like `CUSTOM:`; lower() is already applied so this is fine today — just noting the helper assumes the only namespacing is that single prefix.

2. tests (coverage nit) — add the inverse positive: a matching runtime whose api_key is None should NOT satisfy an aux path needing credentials (currently only identity matching is pinned, not credential presence), since `runtime_api_key = None` flows into resolve_provider_client as explicit-None.
