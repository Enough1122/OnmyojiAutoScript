> AI code review — automated review for reference; please use your judgment.

Excellent loop-breaker: the root cause analysis (vacuous "all parents done" over an empty link set, invisible to `consecutive_failures` because the outcome is `blocked`) is airtight, and the fix layers correctly — exponential backoff honored by `recompute_ready`, escalation to the human `blocked` bucket at the limit, streak/backoff cleared exactly on real progress or completion, and the `has_real_link` check ensuring formally-gated tasks never burn escalation budget. Migration is additive/idempotent and every branch has a test, including the subtle one proving real-link tasks never accumulate streak across repeated blocks. One nit:

- hermes_cli/kanban_db.py:6430 — nit — after escalation, a human who moves the card back to running *without* fixing the cause gets instantly re-escalated on the next block (`dep_streak` starts at the retained limit, no fresh backoff window); that's arguably intended severity, but one sentence in the column comment stating "post-escalation re-blocks skip backoff" would make it read as policy rather than accident.

No blocking issues found.

— reviewer-b (automated review)
