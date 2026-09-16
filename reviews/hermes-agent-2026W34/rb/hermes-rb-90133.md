> AI code review — automated review for reference; please use your judgment.

The inversion is real and the corrected semantics (lower number = more urgent, FIFO within band) match every docstring and the P0–P3 convention; the dispatcher queue, review queue, and default listing are all consistently flipped, and the new regression suite pins ordering, FIFO-within-band, P0 dominance, and both explicit sort directions. Two things beyond the code:

1. **Existing boards invert on upgrade.** Anyone who set priorities while `DESC` was live learned "bigger number = picked first" from observed behavior; after this change their stored values produce the opposite ordering with no error or signal. This deserves an explicit release-note entry ("audit your task priorities; semantic flip") and ideally a one-time `hermes kanban` hint when it detects tasks with priority > 3 (outside the documented P0–P3 band) post-upgrade. A pure code flip is correct but silently reorders every existing board.
2. The second defect (non-spawnable terminal-lane cards consuming the demand-floor slot) is a genuine starvation bug and its test setup is convincing; please confirm the fix composes with the review-lane reservation — i.e. a skipped non-spawnable ready card neither consumes the shared budget nor distorts the review-lane headroom calculation. One combined-scenario test would lock that interaction.
3. kanban_db.py:~3697 — the un-cased fallback `_` branch and `_dispatch_once_locked`'s inline SQL previously matched each other; they still do, but consider deriving both from `VALID_SORT_ORDERS["priority"]` so a future tweak can't update one and orphan the other. (nit)
4. The 10ms sleeps proving created_at independence are the right way to disambiguate priority-vs-recency in these tests. (positive)

No blocking issues found.
