> AI code review — automated review for reference; please use your judgment.

Correct sequencing and ordering: closing stale OPEN rows *before* the ended-only prune unblocks the retention machinery that could never see them (`ended_at IS NOT NULL` hardcoded), rows are closed rather than deleted so transcripts stay searchable until normal retention reclaims them, and the COALESCE idle definition handles all four lifecycle shapes — each pinned by a test including the two NULL-activity edges (brand-new row survives via started_at; dead pre-touch row still closes). Items:

- hermes_state.py:8787 — nit — the 7-day threshold and `idle_auto_close` reason are inline constants; making the days configurable (or at least a module constant) would let long-running eternal-session users tune it without patching, and gives the reason string one source of truth for tooling that wants to special-case reopen.

- hermes_state.py:8795 — nit — if any session flavor skips the `_touch_activity` heartbeat (e.g., a background-ingested transcript-only session), this change silently force-closes it at 7 days; worth one sentence in the docstring naming which writers are guaranteed to touch activity.

No blocking issues found.

— reviewer-b (automated review)
