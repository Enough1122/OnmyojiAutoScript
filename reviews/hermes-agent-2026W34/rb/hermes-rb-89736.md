> AI code review — automated review for reference; please use your judgment.

Small, correct, and tested on both surfaces that matter (overview preview + drill-in rows), including the legacy-NULL → `default` normalization case.

- tui_gateway/server.py:12911 — nit — `or "default"` asserts every untitled-profile row *belongs* to default; if legacy pre-profile sessions should stay distinguishable from explicitly-default ones, returning the raw value and letting the client decide would be safer — fine as-is if the desktop treats them identically.

No blocking issues found.

— reviewer-b (automated review)
