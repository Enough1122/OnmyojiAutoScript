> AI code review — automated review for reference; please use your judgment.

Sensible default with an opt-out story, and the happy-path test asserts the exact wire rows. Items:

- plugins/kanban/dashboard/plugin_api.py:2099 — issue — only the `add_notify_sub` call sits inside the per-home `try`; `_active_profile_name()` and `_configured_home_channels()` run *outside* it, so a malformed/unreadable channels config (or any unexpected probe failure) raises out of the helper — why it matters — the task row is already committed at that point, so the request turns into exactly the misleading HTTP 500 the comment says this helper exists to prevent ("a stale channel configuration must not turn a successfully persisted task into a 500") — suggestion — wrap the entire body (profile lookup + channel enumeration included) in one `try/except` with the same log-and-continue policy.

- tests/plugins/test_kanban_dashboard_plugin.py:1069 — issue (coverage) — the partial-failure branch is untested: no case where one channel's `add_notify_sub` raises asserting (a) status stays 200, (b) the task exists, (c) the *other* home still got subscribed, (d) a warning was logged — why it matters — this except-path is the piece most likely to regress into either a swallowed success or an accidental 500, and it encodes the PR's core promise — suggestion — monkeypatch `kanban_db.add_notify_sub` to raise on the telegram row and pin all four outcomes.

- plugins/kanban/dashboard/plugin_api.py:651 — issue (UX/consistency) — subscription failures are only visible in server logs, while the same response already carries a dispatcher-presence warning field for the UI — why it matters — a user who creates a task while their Telegram route is misconfigured sees silence later with no hint anywhere in the dashboard that auto-subscribe failed at creation — suggestion — collect per-home failures and surface them in the same warnings array the dispatcher check uses.

No blocking issues found — item 1 is the one I'd fix before merge since it contradicts the helper's stated goal.

— reviewer-b (automated review)
