> AI code review — automated review for reference; please use your judgment.

Well-executed part 1 of the split: the private Copilot bridge is lifted verbatim into a shared module (with an in-tree consumer test proving the wire shape didn't change), the two vendor-keyed core decisions become scheme-keyed (`acp://`) so every future ACP client inherits correct defaults — each exclusion pinned *both* ways including the non-ACP-still-upgrades guard — the background-review fork refuses to spawn when the parent's shim cannot carry Hermes tool calls back (fail-safe default: silent clients are assumed capable), and agent-as-provider tool work is spliced into the transcript with the skill-nudge counter ticking through the real `run_conversation` loop. Tests are unusually strong for a refactor. One nit:

- agent/acp_openai_bridge.py:30 — nit — the bare-JSON fallback regex can still match a legitimate JSON object the model prints mid-prose when no `<tool_call>` block exists anywhere in the response (pre-existing behavior, faithfully lifted); worth a comment marking it as accepted ambiguity so a future hardening pass knows it was considered.

No blocking issues found.

— reviewer-b (automated review)
