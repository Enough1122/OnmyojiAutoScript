> AI code review — automated review for reference; please use your judgment.

Right consistency fix: the fire-claim TTL was the only place still hardcoding 300s while every sibling claim derives from `HERMES_CRON_TIMEOUT`; deriving it from `ONESHOT_RUN_CLAIM_TTL_SECONDS` means long-timeout deployments stop re-firing externally-triggered one-shots mid-run, and the stale-claim test now reads the constant instead of a magic 301. One coordination point:

- cron/jobs.py:2605 — issue (coordination) — #89739 (currently open) adds `FIRE_CLAIM_TTL_SECONDS = 300` and makes `get_due_jobs` honor exactly that lease for external one-shot fires; if both merge, there are two constants governing fire-claim lifetime and the sibling-honor window will diverge from the claim default on non-default timeouts — suggestion — reconcile with that PR so one derived constant feeds both the claim and the due-jobs honor check.

No blocking issues found — item 1 is merge-order hygiene, not correctness here.

— reviewer-b (automated review)
