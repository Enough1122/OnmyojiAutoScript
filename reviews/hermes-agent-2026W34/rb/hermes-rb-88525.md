> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): discover secondary profiles' MCP servers in multiplex mode". Correct fix for a real multiplex gap: unscoped discovery only ever connected the DEFAULT profile's mcp_servers, so secondary profiles' declared MCP tools silently didn't exist in gateway turns despite working from the CLI. Re-running discovery under each served profile's `_profile_runtime_scope` (executor off-loop, per-profile failure isolation, default skipped as already covered) is the minimal change, and the `runner.config` vs `config` argument gotcha under systemd is exactly the kind of thing this comment needed to survive refactors. Suggestions:

1. gateway/run.py:30199 (isolation verification) — the fix relies on the process-global server registry being SAFE to share because per-turn `_get_platform_tools()` filters enabled MCP names by the ACTIVE profile's config — please pin that filter with a test (profile B's server must not appear in profile A's turn toolset even though both are connected), since it's now the only line between correct behavior and cross-profile tool leakage.

2. nit — discoveries run sequentially in the default executor, adding one connection round-trip per profile at startup; fine at current scale, but parallelizing per-profile tasks would keep boot time flat as multiplex usage grows.
