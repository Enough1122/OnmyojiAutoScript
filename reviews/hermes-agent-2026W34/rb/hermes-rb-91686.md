> AI code review — automated review for reference; please use your judgment.

The parsing layer is exactly right (inf/nan/negative/garbage all collapse to the safe fallback, and an *invalid* explicit config still defers to A2A_REPLY_TIMEOUT before the 300s default — a nice precedence nuance), the orphan watchdog now provably outlives both the inbound reply window and any routed agent's own timeout, and the test set covers each of those behaviors at the right layer (adapter, wait path, store).

1. `plugins/platforms/a2a/protocol.py:~751–772` (`fail_orphans`) — this signature is being extended **simultaneously by two open PRs**: this one adds `timeout_for=`, while #91688 adds `skip=` (live waiter ids) — why it matters: whichever lands second conflicts textually *and* semantically, and the correct combined behavior is neither alone (skip live tasks AND use per-task limits) — suggestion: coordinate the two merges so the final signature takes both parameters and the watchdog passes both, ideally with one shared test covering skip ∩ per-task-timeout together.

2. `plugins/platforms/a2a/protocol.py:~760–764` — `timeout_for(rec)` executes adapter code **while holding `self._lock`**; today the callback only reads `self._agents`, but the pattern invites future callbacks that touch the same store — why it matters: a lock-ordering inversion here deadlocks the watchdog thread against task writes — suggestion: snapshot records under lock, compute limits outside, re-check before failing; or at minimum document that timeout_for must never call back into the store.

3. `plugins/platforms/a2a/adapter.py:~495–500` — the watchdog warning lost the effective timeout it used to include (the "timeout %ds" fragment), which was genuinely useful when diagnosing "why did my long task get orphaned" — why it matters: now that per-task limits vary, a single global number would be misleading but *no* number hides the answer entirely — suggestion: log the tid plus the result of `self._orphan_timeout_for(rec)`.

Nit: the README table says "prefer gateway.platforms.a2a.extra.reply_timeout" but doesn't state that an invalid explicit value falls back to the env var (not straight to 300) — worth half a sentence given how surprising that ordering could be.

— reviewer-a · automated agent review (Hermes week-review)