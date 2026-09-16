> AI code review — automated review for reference; please use your judgment.

Tight, complete exposure of an existing DB capability to the agent surface: schema `minimum: 1` matches the handler guard, the explicit `isinstance(bool)` exclusion is exactly right (Python `True` is an `int` and would otherwise sneak through as 1), the description documents the per-task override vs board fallback clearly, and the invalid-value tests assert *no row was created* rather than just an error string. Points:

1. No upper bound: `max_retries: 1000000` means a permanently broken task effectively never auto-blocks. Consider a sane ceiling (e.g. reject > 20) or documenting that operators can still intervene manually. (nit)
2. The schema advertises the field to every agent; if only orchestrators should set retry budgets for children, note that there's no per-caller restriction — probably fine given the trust model. (nit)
3. The error message "must be an integer >= 1" doesn't mention that booleans are rejected specifically — models sending `true` will see a correct-but-generic message; adding "(booleans not accepted)" could save a retry round-trip. Very minor. (nit)

No blocking issues found.
