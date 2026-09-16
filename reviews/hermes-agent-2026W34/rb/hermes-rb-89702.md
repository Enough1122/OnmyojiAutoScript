> AI code review — automated review for reference; please use your judgment.

Correct distinction, cleanly drawn: losing *your own* origin thread is a routing fault (stays WARNING), while a fan-out target for a different chat never had that lane to lose (debug) — and both branches are level-pinned by tests so the boundary can't silently move. String-typed chat_id comparison avoids int/str mismatches across adapters.

— reviewer-b (automated review)

No blocking issues found.
