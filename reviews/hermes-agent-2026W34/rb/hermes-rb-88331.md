> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-bounded fix for unbounded state.db growth and BOTS/SESSIONS duplicate flooding (#88268): retention resolves env > config > default(50) with invalid values warned about, the prune's id-range scan `[prefix, prefix_hi)` scales with the excess rather than the whole cron pile, the deletion cascade mirrors `delete_session` exactly (delegate children → orphan branches → messages → row, plus unreferenced system-prompt cleanup), everything runs inside `_execute_write`'s lock/jitter handling, and a failure can never wedge the run's bookkeeping or delivery. Tests cover newest-kept ordering, cross-job isolation, non-cron-session safety, and the keep=0 edge.

Nit (non-blocking): cron/scheduler.py — the prune executes after **every** fire even when there's nothing to remove (a 1-minute job under its retention pays one wasted SELECT per tick). A cheap early-out — fetch victim ids first and skip the write transaction when empty — would keep hot jobs at zero write cost in the common case; alternatively only attempt pruning every Nth fire.
