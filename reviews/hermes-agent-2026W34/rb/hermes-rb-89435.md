> AI code review — automated review for reference; please use your judgment.

Correct un-wiring of an accidental CLI-only restriction: `_emit_status` resolves its surface at emission time, so handing the memory provider the same bound method on every platform is safe for gateway/TUI construction order, and the renamed test proves the late-binding contract directly (assigning `agent.status_callback` *after* init still delivers). The removed stale NOTE block was already describing dead behavior.

— reviewer-b (automated review)

No blocking issues found.
