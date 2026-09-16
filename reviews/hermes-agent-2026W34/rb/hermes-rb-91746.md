> AI code review — automated review; please use your judgment.

1. `plugins/platforms/email/adapter.py:~852–862` vs `~828–831` — **the new exponential backoff can never take effect**: `_check_inbox()` sets `self._last_fetch_failed = False` on the failure path *before returning*, so the poll-loop guard `if not self._last_fetch_failed: self._poll_backoff = 0.0` fires right after the backoff was bumped and zeroes it — why it matters: every failed poll sleeps only `_poll_interval`, silently reintroducing the Gmail hammering this PR exists to stop — suggestion: have `_check_inbox` return/report success explicitly (e.g. return `bool`, or count `_consecutive_failures`) and only reset backoff on an actually-successful check.

2. `plugins/platforms/email/adapter.py:~850` — removing the `_set_fatal_error`/`_notify_fatal_error` escalation entirely means a mailbox that stays broken (expired app password, disabled IMAP) now degrades to log warnings forever while the platform reports healthy — why it matters: users lose the existing reconnect/status surface and may go weeks without noticing dead email delivery — suggestion: keep the resilient in-loop retry but escalate through the fatal hook only after N consecutive failures (e.g. 10), preserving both decoupling and observability.

3. `plugins/platforms/email/adapter.py:1183, 1298, 1378, 1474` — the display name `"Hermes Agent"` is hardcoded in four independent places — why it matters: any rename/localization or user preference requires four synchronized edits, and the four sites will drift — suggestion: hoist a module-level constant (or an `EMAIL_DISPLAY_NAME` config knob) and use it in all senders including `_standalone_send`.

4. `plugins/platforms/email/adapter.py:559` — default poll interval changes 15s → 60s for *all* deployments, not just datacenter/Gmail ones, and this PR touches no docs — why it matters: worst-case new-mail latency grows 4x silently and config-default references elsewhere will disagree with the code — suggestion: update the email plugin docs/config template in this PR, or keep the global default and apply the longer interval only when a Gmail host is detected/configured.

5. `plugins/platforms/email/adapter.py:~681, ~877` — raising IMAP socket timeouts 30s → 300s on calls that run on the **default** shared executor means one slow Gmail login can pin a worker thread for 5 minutes — why it matters: other platforms sharing the default executor lose concurrency headroom during exactly those stalls — suggestion: use a dedicated single-thread executor for IMAP work, or keep connect/login timeouts modest (60–90s) and let the (fixed) backoff handle pacing.

Nit (`~825–835`): non-IMAP poll exceptions (dispatch errors etc.) are retried at bare `_poll_interval` with no backoff, unlike IMAP failures — consider applying the same backoff to the generic `except` branch for consistency.

Overall: the executor-offload refactor of the connect test and the fd-leak-preserving extraction look correct, and the reconnect UID-baseline restore is nicely preserved. Item 1 is a functional bug that should be fixed before merge; item 2 is a judgment call worth an explicit decision.

— reviewer-a · automated agent review (Hermes week-review)
