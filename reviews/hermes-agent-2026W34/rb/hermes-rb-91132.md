> AI code review — automated review for reference; please use your judgment.

1. `agent/agent_runtime_helpers.py:~966–968` (`_remint_command_token`) — the once-per-lifetime guard is keyed by ````getattr(agent, "provider", "") or ""````, so an unnamed (`provider=""`) or identically-named key_cmd source shares one bucket across *different* token sources — why it matters: in a fallback chain where two distinct `key_cmd` providers lack explicit names, the first auth failure permanently consumes the single re-mint for the second source too, which then can never recover even though its credential is fine — suggestion: key on `(provider, id(source))` or the source's configured command string, so the bound is per-credential rather than per-name-collision.

2. `agent/agent_runtime_helpers.py:~963–974` — the guard is process-eternal: a legitimately rotated credential that fails auth again hours later gets no further re-mints until restart, replacing "stuck until TTL" with "one retry, then stuck" — why it matters: brokers that revoke-and-reissue on a schedule will hit exactly this on their second rotation — suggestion: keep the anti-spin property but make it temporal (allow a new re-mint after e.g. 10× the advertised TTL, or N per hour), which preserves the no-spin guarantee against instantly-revoked tokens while surviving normal rotation cadence.

3. Nit (`:~949`): 403 is treated as auth alongside 401; some gateways use 403 for quota/permission states where re-minting is wasted work — harmless today precisely because the guard is once-only, but worth revisiting if item 2 introduces re-arming.

Otherwise very strong: `invalidate()` is correctly lock-guarded and minimal, the auth-classification matrix (classified / auth_permanent / bare 401 without classification) is fully tested, non-auth reasons are proven inert, static-key/None/non-callable sources are untouched, a raising `invalidate` degrades to no-recovery rather than breaking the turn, and the counting-source fixtures make every assertion observable (helper ran exactly twice, not three times). Items 1–2 shape the recovery lifetime, not the mechanism.

— reviewer-a · automated agent review (Hermes week-review)
