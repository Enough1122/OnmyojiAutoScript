> AI code review — automated review for reference; please use your judgment.

Great observability fix with the hard part handled: threading `board` from the dispatch tick through to `read_worker_log` so the diagnosis works on every board (not just whichever is "current" for the dispatching thread) — and there's a dedicated regression test reproducing exactly that gateway-thread scenario, plus the payload carries `worker_output` for telemetry, not just the human-readable error string. The 400-char cap and never-raise contract keep the reap path safe.

— reviewer-b (automated review)

No blocking issues found.
