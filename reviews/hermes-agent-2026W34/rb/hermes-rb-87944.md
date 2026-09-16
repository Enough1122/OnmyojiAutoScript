> AI code review — automated review for reference; please use your judgment.

Review of "fix(sessions): reclaim deleted-session data during vacuum". Well-bounded GC for legacy databases: old versions left messages behind when their session row was removed, keeping both `messages` and FTS5 indexes alive forever. The implementation does it right — canonical-table deletes so existing FTS triggers clean the search indexes, batched transactions (10k default) so an upgraded multi-million-row DB doesn't build one giant WAL commit before VACUUM, loop-until-short-batch termination, and tests proving FTS entries disappear while live-session messages survive. One nit:

- hermes_state.py:prune_orphaned_messages — rows with a NULL `session_id` also satisfy `NOT EXISTS` and will be collected; if that's impossible in practice it's fine, but if any code path ever writes headless rows intentionally this GC silently eats them — worth one comment stating the column's nullability contract.
