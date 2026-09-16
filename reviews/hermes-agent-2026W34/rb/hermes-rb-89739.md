> AI code review — automated review for reference; please use your judgment.

Correct fix with a genuinely end-to-end test: process A claims + dispatches + heartbeats at second 290, process B ticks at 301 and must neither re-list the job as due nor delete the finite record, while the owner's fenced terminal update still lands. The `0 <= claim_age` clock-skew guard and the malformed-claim pass-through are both the right calls. Items:

- cron/jobs.py:3196 — issue (verification) — the lease honor is scoped to `schedule.kind == "once"`; if external/manual fires can also target *recurring* jobs (the fire-claim machinery itself isn't once-specific), a sibling scheduler can still re-dispatch or prune a recurring job whose external run is inside a fresh lease — why it matters — same deletion-mid-run bug, different schedule shape — suggestion — either confirm external fires are once-only by construction and say so in the comment, or drop the kind gate and honor any fresh `fire_claim`.

No blocking issues found.

— reviewer-b (automated review)
