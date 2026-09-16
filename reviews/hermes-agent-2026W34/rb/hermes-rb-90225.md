> AI code review — automated review for reference; please use your judgment.

Review of "fix(kanban): let a deliberate re-queue clear the active_pr respawn guard". Thoughtful resolution of the review-lifecycle deadlock: the active-PR guard now yields only to EXPLICIT operator/reviewer intent (`promoted_manual`, `unblocked`, `changes_requested`, `review_reopened`), while automatic recovery events stay able to clear `recent_success` but can never defeat duplicate-PR protection (crashed-worker-opened-PR case called out explicitly). The whole-second timestamp problem is handled properly via the new comment_id→event binding with a documented legacy fallback. Suggestions:

1. hermes_cli/kanban_db.py:9420 (tier-drift risk) — `_ACTIVE_PR_CONTINUATION_EVENT_KINDS` must remain a subset of `_RESPAWN_REQUEUE_EVENT_KINDS` for the tiering to make sense; nothing enforces it — add a trivial test asserting subset relations (and that both cover the docstring's lifecycle list) so a future event kind lands in the right tiers.

2. hermes_cli/kanban_db.py:9450 (_comment_event_id scan) — the binding lookup walks every `commented` event newest-first per guard evaluation; fine at human comment volumes, but it runs inside the dispatcher hot path — consider an indexed `comment_id` column on task_comments (or caching the mapping) if boards grow chatty.

3. hermes_cli/kanban_db.py:9475 (legacy fallback contract) — equal-second authority is reserved for "the CLI's own UNBLOCK comment", which quietly defines a text-format contract for external tooling that wants the same privilege — document the accepted comment shape (and why raw API comments can't claim it) wherever the unblock command is documented.

4. hermes_cli/kanban_db.py:9396 (nit, doc duplication) — the event-kind taxonomy is now described three times (constants block, _requeued_since docstring, check_respawn_guard docstring); keep the canonical table in ONE place and reference it, or the lists will drift from their prose.
