> AI code review — automated review for reference; please use your judgment.

This fixes a real silent-failure class with an unusually clean design: `origin_requested_{model,provider}` are written once at init as an immutable audit snapshot (with a docstring correctly explaining why `requested_provider`'s fallback-time reassignment makes it unfit for auditing), the session row records the swap best-effort without ever letting bookkeeping abort recovery, and one-shot runs get a loud real-stderr warning that keeps stdout byte-stable for parsers. Points:

1. hermes_cli/oneshot.py:_annotate_requested_route (~220) reads `agent._fallback_activated` — please confirm that attribute is set *inside* `try_activate_fallback` itself so all three activation arms (rate-limit, transport, empty-content retry) flag identically; if any arm sets a local variant or forgets, that surface silently reports `fallback_activated: false` while serving the fallback — recreating the bug this fixes for exactly those routes.
2. The stderr warning fires even when the run subsequently failed (placed before the failure branch) — good; consider appending the failover `reason` code to the line so on-call can distinguish quota vs transport at a glance.
3. `record_session_fallback` being a no-op when the lazy row doesn't exist yet, with `_ensure_db_session` re-applying, is the right shape — add one test covering that exact ordering (fallback on the very first turn), since it's the documented-but-untested seam. (nit)
4. Usage-file additions are purely additive keys, so existing pipeline consumers won't break; the docstring's "assert fallback_activated is false" guidance is a nice operational contract for reproducibility-sensitive callers. (positive)

No blocking issues found.
