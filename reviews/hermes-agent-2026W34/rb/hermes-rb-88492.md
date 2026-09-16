> AI code review — automated review for reference; please use your judgment.

Review of "fix(kanban): bound default worker concurrency". Right distinction drawn between a PER-TICK spawn budget (`max_spawn`) and a LIVE concurrency ceiling (`max_in_progress`, default 3) — a backlog previously burst-spawned unbounded workers regardless of tick size. Propagation reaches both entry points (gateway daemon and standalone `run_daemon`), config parsing tolerates None/junk/negative by falling back to unlimited, and the new tests pin the default value plus daemon→dispatch propagation. Suggestions:

1. hermes_cli/kanban_db.py:run_daemon (verify enforcement) — the daemon now FORWARDS `max_in_progress` to `dispatch_once`, but no hunk here shows `dispatch_once` accepting or enforcing it, and the propagation tests inject a FAKE `dispatch_once` that merely captures kwargs — please confirm the real `dispatch_once` both accepts the parameter and actually counts in-flight workers against it (an accepted-but-ignored kwarg would make the new default purely cosmetic).

2. nit — the 15-line inline tolerant-config-parse block in `_ready_queue_nonempty`'s sibling duplicates the resolver pattern used elsewhere for kanban knobs; a `_kanban_int_setting(name)` helper would shrink it and standardize the "invalid ⇒ unlimited" semantics.
