> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Clean stdlib-only implementation with sensible provider normalization and decent test coverage. A few issues worth addressing:

- **debug_trajectory.py:116-136 (`analyze_tool_usage`) — error attribution is per-*event*, not per-tool_call.** `status`/`error` are read from the parent event, so one event carrying three tool calls with one failure marks all three as errors; conversely, if Hermes records tool *results* in separate follow-up events (typical transcript shape), planner-side status won't reflect tool failures at all. Why it matters: the "tool reliability" report this skill exists to produce would be wrong on real data. Suggestion: attribute status from each call's own result entry (e.g. `tc.get("status")`/`result.error`) and fall back to event-level only when absent.

- **debug_trajectory.py:24-38 (`load_transcript_events`) — malformed lines vanish silently.** `except Exception: continue` drops unparsable JSONL lines with no counter, no warning. For a *debugging* tool this quietly poisons every downstream metric (`total_steps`, hit rates) while appearing healthy. Suggestion: collect malformed line numbers and surface them in both JSON and human output (`malformed_lines: [..]`), even if analysis continues.

- **debug_trajectory.py:76-86 — cache-bust detection has no minimum-turn-size floor.** A tiny turn (say 40 prompt tokens, 0 cached) reports 0% and trips a "bust," while noise on small turns dominates the signal; token-weighted overall rate doesn't have this problem. Suggestion: require `prompt_tokens >= some floor` (configurable, e.g. 500) before a per-turn rate participates in bust detection.

- **Schema assumptions are undocumented and brittle.** The parser expects top-level `type` ∈ {USER_INPUT, PLANNER_RESPONSE}, flat `usage`/`token_usage`, and `tool_calls` as a list — but never validates or documents the contract, and there's no tolerance for nested `message`-style transcripts. Since the fixtures in the tests are self-invented, green tests don't prove compatibility with real `transcript.jsonl` files. Suggestion: document the expected schema in SKILL.md and/or accept a couple of common shapes explicitly.

- **debug_trajectory.py:196,201 — emoji output breaks on Windows consoles.** `⚠️`/`✓` raise `UnicodeEncodeError` under cp1252 stdout, yet the skill declares windows support. Suggestion: ASCII markers (`[WARN]`/`[OK]`) or guard with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

- **tests/skills/test_trajectory_debugger_skill.py — coverage gaps.** Untested: malformed-line behavior (ties to point 2), nonexistent-file path (`FileNotFoundError`), Anthropic-key normalization (`cache_read_input_tokens` branch), empty transcript, threshold boundary (rate == threshold). Each is cheap to add and pins real requirements.

Nit: debug_trajectory.py:224-238 — `turn` dumps full content/tool payloads unbounded; a `--max-chars N` truncation default (~4k) would keep terminal sessions usable on big steps.
