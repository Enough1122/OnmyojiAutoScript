> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct policy layering with the right failure posture: profile-level `cron.default_delivery` overrides only when the job didn't ask explicitly, an *unrecognized* value is refused at creation with a warning rather than stored to silently drop every future run's output, and the six tests cover precedence in both directions, no-origin fallback, multi-target values, and the invalid-value warning path. Findings below are minor:

1. cron/jobs.py:_is_valid_default_delivery — the accepted-token set (`origin`/`local`/`all`, platform names via `_is_known_delivery_platform`) partially re-encodes what `cron.scheduler._resolve_delivery_targets` consumes; the two can drift (e.g. scheduler gains a new sentinel token that this validator then rejects). Since this module already imports from `cron.scheduler`, export one shared `is_valid_delivery_spec(value)` from the scheduler and call it here — the import-failure degenerate branch could then shrink to "reject anything non-trivial" instead of hardcoding its own mini-allowlist.
