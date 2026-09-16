> AI code review — automated review for reference; please use your judgment.

The change itself is right: a 429 whose body proves deterministic billing exhaustion must not burn a ~40–50 minute Retry-After retry budget, and placing the check ahead of the OpenRouter upstream disambiguation is correctly reasoned and tested. Two things:

- **PR title** — issue — the title is the literal error string `unexpected end of JSON input`, almost certainly captured from a failed tool invocation instead of the intended commit subject — why it matters — this is exactly the class of accident the change fixes, and as-is it poisons changelog generation and every future search for the monthly-cap behavior — suggestion — retitle to something like `fix(error-classifier): treat 429 monthly-spend-cap bodies as billing (#91091)`.

- agent/error_classifier.py:1273 — issue (verification) — `_BILLING_PATTERNS` entries are lowercase while the match runs against `error_msg`; please confirm that variable is normalized to lowercase upstream of this point — why it matters — Anthropic's actual body capitalizes ("...your account's monthly spend limit..." arrives lowercase in the test fixture via MockAPIError, but real SDK messages may differ), and a case mismatch makes the new branch dead code in production while tests stay green — suggestion — one assertion with mixed-case input (`"Monthly Spend Limit"`) settles it.

No blocking issues found — item 1 before merge please, item 2 is a one-line check.

— reviewer-b (automated review)
