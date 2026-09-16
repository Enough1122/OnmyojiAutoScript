> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): report the conversation category even when it is empty". Carefully reasoned UX fix in three coordinated layers: the backend keeps a zero-token `conversation` row in the payload (an empty transcript was indistinguishable from "never measured"); the BAR drops zero-token segments (a min-w-px sliver would paint invisible width — the comment explains exactly why) while the LIST below still names them; and a new `stale` flag labels pre-turn estimates as such during a running turn, with tests covering the busy→idle transition AND the busy-from-start edge where labeling an empty panel as stale would be wrong. The rationale comments cite the gateway's turn-start history snapshot to justify why refetching can't help. Suggestions:

1. agent/context_breakdown.py:_ALWAYS_REPORTED (nit) — good extension point; consider also documenting WHY conversation is the only always-reported member today (every session has turns) so future additions argue from the same principle.

No blocking issues found.
