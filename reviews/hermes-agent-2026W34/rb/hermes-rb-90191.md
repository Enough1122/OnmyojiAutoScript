> AI code review — automated review for reference; please use your judgment.

Review of "feat(agent): opt-in wall-clock and token usage limits per turn/session". Well-scoped safety belt mirroring the tool_guardrails pattern: pure observer tracker, the loop owns breaking, disabled-by-default, junk-tolerant config parsing, monotonic clock, and the session-watermark trick makes turn budgets retry-surviving (usage already counted stays counted). Tests cover config edge cases and tracker behavior. Suggestions:

1. agent/usage_limits.py docstring / conversation_loop.py:1952 (accounting completeness) — both ceilings key on `agent.session_total_tokens`; if ANY provider call path fails to update that aggregate (e.g. inline streaming or auxiliary compression calls), the token belts silently under-count and a runaway session keeps burning past its limit — worth one verification pass (or an assert-style test) that EVERY API-call site feeds the aggregate, especially the newer direct/streaming variants.

2. conversation_loop.py:1955 (boundary enforcement) — checks run only between loop iterations, so a single slow generation can overshoot the wall-clock ceiling arbitrarily before the next boundary notices — fine as designed ("belts, not preemption"), but say so explicitly in the config docs so users don't expect mid-call cancellation.

3. agent/usage_limits.py:_limit (nit) — `int(True)` is 1, so a YAML `turn_total_tokens: true` typo enables a 1-token ceiling that trips immediately — reject bools explicitly alongside the junk values the tests already cover.
