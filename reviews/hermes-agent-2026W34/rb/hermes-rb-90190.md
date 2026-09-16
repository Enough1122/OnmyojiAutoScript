> AI code review — automated review for reference; please use your judgment.

Review of "feat(guardrails): detect alternating tool-call cycles (loop_tool_cycle)". Fills a real gap — successful alternating loops (A,B,A,B across mutating tools or varying reads) were invisible to all four existing guards. The implementation is tight: smallest-period-first scan with ≥2-distinct-signature requirement (mono loops correctly left to the exact-failure/no-progress guards), blocked-before-call executions excluded from history so the pattern isn't extended by refusals, warn-only-as-fallback so a call never stacks two warnings, and bounded scan math (window 25 × max period 8). Suggestions:

1. agent/tool_guardrails.py:88 (config can promise what the window can't deliver) — with `_CYCLE_WINDOW = 25`, `tool_cycle_block_repeats` can never fire for period×repeats > 25 (e.g. an 8-call cycle at the default block_repeats=4 needs 32 entries); from_mapping happily accepts larger user values that then silently do nothing — either clamp/validate block_repeats ≤ window // max_period at parse time, or scale the deque from the configured values, and document the effective ceiling.

2. agent/tool_guardrails.py:366 (ordering note) — in before_call the cycle check now runs BEFORE the exact-failure/same-tool guards; a two-tool loop where both calls also fail identically reports loop_tool_cycle rather than the more specific failure codes — probably the right precedence (cycle is the broader truth), but pin it with one test so a future reorder is deliberate.

3. tests/agent/test_tool_cycle_guard.py (coverage nit) — add a case where a cycle is interrupted mid-pattern (A,B,A,B,A,X,A,B…) to prove the detector resets cleanly and doesn't fire on partial residue after the tail breaks.
