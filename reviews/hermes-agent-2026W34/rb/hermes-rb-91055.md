> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right fix for a nasty double-compaction: the rough estimator ran immediately after an idle boundary and judged the *just-compacted* transcript against the same threshold, archiving/re-inserting the protected tail twice and duplicating active completion rows. Suppressing the turn-start preflight once an idle boundary succeeded — and letting the next real provider request adjudicate with actual usage — matches the existing \`_should_run_preflight_estimate\` gating philosophy. The regression test asserts exactly the right invariants (one compression call, transcript length intact, \`should_compress\` never consulted).

Nit-level only:

- **tests/agent/test_idle_compaction_lock_and_guards.py:~191 — add a "not sticky" assertion.** The fix's safety depends on the suppression being scoped to *this* prologue invocation, not latched onto the agent across turns. One extra pair of lines in the same test (call \`_run_prologue\` a second time with \`preflight_estimate=True\` after resetting \`_compress_context\`/\`_last_activity_ts\` to now) proving prefire fires again would pin that a future refactor can't accidentally hoist \`_idle_compacted\` into an instance attribute.

- **agent/turn_context.py:~851 — consider naming/commenting the flag as "boundary already adjudicated this turn"** rather than "idle compacted," since the semantic guarantee being encoded is about adjudication, not the mechanism; helps whoever touches the preflight gate next.

No blocking issues found.