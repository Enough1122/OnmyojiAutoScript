> AI code review — automated review for reference; please use your judgment.

Well-targeted fix: every truncation early-return sat *before* the finish_reason=stop kanban guard, so workers could exit rc=0 with no terminal board call — now all five sites route through the same bounded nudge, strict role alternation is preserved by closing the trailing tool result first, and the first-message case is correctly gated off for Anthropic/Bedrock where two consecutive user turns are rejected. Tests cover append-and-continue, the two-attempt bound, inertness outside kanban workers, and already-terminal sessions.

- agent/conversation_loop.py:1053 — issue (verification/doc) — `_kanban_stop_nudges` is shared with the finish_reason=stop guard's counter (per the docstring), so a worker that got one stop-path nudge earlier in the session has only one truncation nudge left — why it matters — that coupling is deliberate budget-sharing but invisible at the five new call sites; one sentence in the helper docstring ("shares the session-wide 2-nudge budget with the stop guard") would prevent someone from 'fixing' the counter into a second independent one later.

- tests/agent/test_kanban_stop.py:92 — nit (coverage) — all coverage is at the helper level; there's no test that a break+`restart_with_kanban_stop_nudge` cycle actually re-enters the API loop against the nudged history (the wiring could regress independently of the helper). Heavier harness, so fine as a follow-up.

No blocking issues found.

— reviewer-b (automated review)
