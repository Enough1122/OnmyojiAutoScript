> AI code review — automated review for reference; please use your judgment.

Review of "fix(kanban): preserve stderr when workers crash during startup". High-value diagnostics: a run-boundary marker is appended to each worker's log at spawn, and crash/spawn-failure events now embed a REDACTED, bounded tail of only THAT run's bytes — the backward marker search correctly spans chunk boundaries via an overlap suffix, the tail trim respects UTF-8 continuation bytes after re-encoding, and the payload rides through every spawn-failure site plus `detect_crashed_workers` (with `board` threaded so multi-board dispatchers read the right directory). Tests cover the new diagnostics module. Suggestions:

1. hermes_cli/kanban_db.py:_read_worker_run_log_tail (marker-less runs) — when `current_run_id` is None the function returns None and the crash event ships WITHOUT any stderr evidence; that's exactly the legacy/pre-marker population most likely to be crashing — consider falling back to a plain bounded tail (still redacted) when no marker exists, tagged `provenance: pre-marker`.

2. nit — the 64KB scan chunk size vs 16KB tail budget means up to ~4× over-read per crash event; harmless at this scale, just noting the constants are coupled if either changes.
