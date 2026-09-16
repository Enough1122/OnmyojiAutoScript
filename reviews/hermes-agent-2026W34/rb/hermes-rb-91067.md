> AI code review — automated review for reference; please use your judgment.

Right fix — the clamp was correct but invisible, and naming `compression.threshold` in the message is what makes it actionable. Test coverage including the two *no-warning* negatives is exactly right.

- agent/context_compressor.py:2933 — issue — `_effective_threshold_percent` runs on every threshold evaluation, so a user sitting on a small-context model with a low configured value gets this WARNING on every single check/compaction pass for the life of the session — why it matters — repeated identical warnings train users to ignore the log channel precisely when a *different* compression warning matters — suggestion — dedupe: emit once per distinct (threshold, floor) pair per process (a tiny module-level `_warned_floors: set`), or downgrade repeats to debug level after the first.

No blocking issues found.

— reviewer-b (automated review)
