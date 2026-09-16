> AI code review — automated review for reference; please use your judgment.

Review of "feat(plugins): adaptive-reasoning" (sampled: classifier/config/middleware wiring in the 777-line module plus the test file; the closed-loop llm_execution observer was reviewed at its contract seams). Standout plugin engineering: the docstring reports MEASURED A/B data instead of vibes, states its own blind spot (short-and-hard prompts route low; real accuracy loss observed) alongside built-in mitigations (tool-error escalation, floor=medium escape hatch), keeps the prompt-cache prefix untouched by rewriting only the request-scoped effort field, handles the CJK \b-boundary pitfall explicitly, adds a closed-loop observer with an anti-oscillation guard for 3-tier scales, and forgets stale turn counters. Config caching on (mtime_ns, size) matches core conventions; floor>ceiling self-corrects. Suggestions:

1. tools/delegate_tool-adjacent concern — `_session_work_depth` reads full message history per call on every API call of every turn when enabled; for long sessions consider bounding the scan to the tail window that actually feeds classification.

2. nit — session tool-error counters are keyed (session_id, turn_id) in a plain dict; `_forget_stale_turns` bounds staleness, but a hard cap on map size would future-proof against id-churn.

3. nit — EFFORT_SCALE is duplicated from hermes_constants.VALID_REASONING_EFFORTS "mirrored"; import it so scale additions can't fork the two lists.
