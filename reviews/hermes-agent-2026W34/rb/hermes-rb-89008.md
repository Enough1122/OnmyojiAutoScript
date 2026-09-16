> AI code review — automated review for reference; please use your judgment.

Right fix for a genuinely misleading failure: a SIGKILLed updater (external restart killing its cgroup) never writes `.update_exit_code`, so polling to the full timeout and reporting "timed out" blamed latency for what was actually a death. The dead-pid signal is sound — the driver holds the lock for its whole run and only clean exits remove it — and covering *both* the streaming watcher and the post-restart notification path closes the second window where the stale lock was previously invisible. Points:

1. gateway/run.py — the ~25-line dead-updater block is duplicated verbatim in `_watch_update_progress` and `_send_update_notification`. Extract `_updater_died_without_exit_code() -> bool` (and have callers do the write/unlink); the pair will otherwise drift exactly like earlier duplicated guards in this codebase.
2. PID-reuse direction is safe-by-accident: a recycled pid makes the checker report "alive" and degrades to the old slow timeout rather than falsely failing a live run. Worth one comment stating that bias, since the natural "improvement" (checking /proc cmdline) would introduce its own races. (nit)
3. The synthesized exit code "1" loses the distinction between "failed with rc" and "was killed"; consider writing a sentinel (e.g. "killed") or logging the lock pid alongside — item already half-covered by the WARNING naming the pid. (nit)
4. The elapsed-time regression test (<2s vs old 30-minute behavior) plus the live-pid non-interference test are precisely the right pair. (positive)

No blocking issues found.
