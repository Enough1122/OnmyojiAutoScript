> AI code review — automated review; please use your judgment.

Small, correct addition: `_get_usage` now surfaces `cache_read_tokens`/`cache_write_tokens` through the same `g()` fallback helper as the neighboring counters, the TS `UsageStats` type gains both as optional fields (so older agents without the attributes simply omit them), and a focused test pins the mapping on a bare agent namespace.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
