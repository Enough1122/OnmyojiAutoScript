> AI code review — automated review for reference; please use your judgment.

Correct root cause and complete fix: the capability-triggered Bot Chat rebuild called `_make_agent` without any of the session's own picks, so `_make_agent`'s config-default fallbacks silently discarded an explicit `/model` pin, reasoning choice, or tier. Threading exactly the three override fields (omitting absent ones rather than manufacturing empty overrides — both behaviors pinned), plus the one-turn-restore guard that defers the sync instead of discarding an in-flight `--once` switch, closes both halves of the bug. The comment explaining why `bot_caps_seen` deliberately does *not* advance on skipped turns is the detail that makes the deferral self-healing rather than lossy.

— reviewer-b (automated review)

No blocking issues found.
