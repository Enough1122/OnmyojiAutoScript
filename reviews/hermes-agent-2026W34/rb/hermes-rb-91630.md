> AI code review — automated review for reference; please use your judgment.

Right fix for a real wedge: an unbounded `await close_async()` inside the reconnect lock turned one bad teardown into a permanently dead connection, and bounding it while still starting the replacement restores liveness. The hang test pins the behavior nicely.

- plugins/platforms/slack/adapter.py:1343 — issue — after a teardown timeout the *old* handler is abandoned, not stopped: its socket task and listener keep running while the replacement connects — why it matters — Socket Mode then has two live clients for a window; Slack round-robins WSS deliveries across connections, so this shows up as duplicated inbound events (double agent turns) precisely on flaky-network instances where reconnects are frequent — suggestion — escalate after the timeout instead of walking away: grab the handler task reference and `task.cancel()` (+`suppress(asyncio.CancelledError)`) before starting the replacement, or at minimum document/track the overlap so duplicate suppression can cover it.

- tests/gateway/test_slack_socket_reconnect_heal.py:299 — nit (coverage) — only the timeout branch is exercised; the `except Exception` path (close raising synchronously-ish) and the assertion that the reconnect lock is released afterwards (a second `_restart_socket_mode` acquires promptly) would pin the "lock never wedges" property the docstring promises rather than just single-shot recovery.

No blocking issues found — item 1 is worth deciding deliberately since it trades a hang for possible duplicate deliveries.

— reviewer-b (automated review)
