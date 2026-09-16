> AI code review — automated review; please use your judgment.

1. `tools/mcp_tool.py` (`_get_circuit_breaker_config`) — ````bool(cb_config.get("enabled", True))```` treats any non-empty *string* as enabled, so an env/JSON override spelling ````"false"```` keeps the breaker armed while the operator believes it's off — why it matters: this is precisely the "models burn 100+ iterations retrying a dead server" failure the knob exists to stop, and other recent config surfaces added explicit string coercion for this exact reason — suggestion: reuse the shared bool-coercion helper (or accept `{"false","0","no","off",""}` as False).

2. `tools/mcp_tool.py` (`_get_circuit_breaker_config` call sites) — the config is read inside `_bump_server_error` (every failure), the tool-handler gate (every MCP tool call), and the short-circuit branch; the docstring leans on `load_config_readonly` caching — why it matters: if that loader does an mtime/stat per call, hot tool paths gain measurable latency; if it caches forever, a live `hermes config set` won't apply until restart, contradicting the configurability story — suggestion: verify which it is and either rely on the documented cache or snapshot settings once per server-connect with a cheap TTL.

3. Nit: the default triplet now lives in three places (module fallback constants, `config_defaults.py`, `cli-config.yaml.example`) — the module constants already serve as the single fallback source, so a comment cross-referencing them from the other two would prevent silent drift.

The behavior matrix is well tested end-to-end through the real handler: disabled-mode still tracks error counts without ever opening the breaker, custom threshold trips at exactly 5, custom cooldown gates then releases the half-open probe and resets on success, and invalid values clamp sanely (threshold→1, negative cooldown→0). Replacing the module constants with config reads while keeping them as fallbacks is a clean backward-compatible migration.

— reviewer-a · automated agent review (Hermes week-review)
