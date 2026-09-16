> AI code review — automated review for reference; please use your judgment.

1. `plugins/platforms/a2a/adapter.py:~962–995` (`_wait_in_background`) — one **daemon thread per background task**, blocked on `fut.result()` with no timeout at all, while the watchdog now *skips* any task id with a live waiter — why it matters: a hung gateway turn that never resolves its future produces an immortal combination — a blocked thread, a permanently non-terminal task, and zero watchdog recourse; many long jobs over days of uptime accumulate zombies — suggestion: bound the background wait (`fut.result(timeout=<generous ceiling>)`, e.g. hours, then finalize as failed) or use a shared bounded executor; alternatively let the watchdog fail live tasks after a much larger second threshold.

2. `plugins/platforms/a2a/tools.py:~357–366` (`a2a_get_task`) — every poll re-fetches the Agent Card (`_fetch_card`) before the JSON-RPC call — why it matters: a model polling every few seconds turns card fetches into most of the traffic to the peer, and each fetch is another failure surface — suggestion: reuse the existing per-peer card cache (with TTL) that other call sites use, or cache within the tool for the process lifetime keyed by base URL.

3. `plugins/platforms/a2a/tools.py:~229–232` (`_send_task`) — for in-progress states the reply is deliberately not persisted and no metric fires; the terminal outcome lands in the store only if someone actually calls `a2a_get_task` until completion — why it matters: an unpolled job leaves no trace in `a2a_history` and undercounts inbound totals, so history quietly diverges from what actually happened — suggestion: record the accepted task (state=working) immediately with a marker, and update it on poll; or document the gap in DESIGN.md so it's a known property rather than an oversight.

4. Nit (`tools.py:~371–376`): GetTask params send both `id` and `taskId` — reasonable peer-compat hedge, but a one-line comment saying which spec version expects which would stop the next reader from 'fixing' it; same for `unwrap_send_message_response` being applied to a GetTask result (works because both share the Task envelope — say so).

Overall: strong feature work — the inbound returnImmediately path (flag parsing incl. legacy `blocking:false`, background waiter, cancel-race-safe finalize), the watchdog skip, the new outbound poll tool, schema/registration tests, and complete docs all hang together; item 1 is the one real resource-lifetime question I'd settle before merge.

— reviewer-a · automated agent review (Hermes week-review)
