> AI code review — automated review for reference; please use your judgment.

Reviewed the gate-bypass logic end to end: the `force` override correctly skips only the ambient focus/visibility gate, the listener triggers strictly on a non-`success` → `success` transition (so re-entering polling or error states can't spuriously poll), the pending timer is cleared before the forced pass, cleanup unsubscribes, and the forced refresh still reschedules the normal focus-gated cadence afterward — background polling is not resurrected by this path. Both new tests pin exactly the regression (stale failure clearing while unfocused) and the negative case (non-success transitions must not poll), which is the right pair.

No blocking issues found.

Nit (`use-status-snapshot.ts:~110–115`): the string literal `'success'` is matched against the onboarding store's flow-status union here and set in tests elsewhere; importing a shared `FLOW_STATUS` const/type from `@/store/onboarding` would make a future rename a compile error instead of a silently dead listener. (Multi-window installs will run one listener per window and each forces its own refresh — harmless duplicate RPCs today, just worth knowing.)

— reviewer-a · automated agent review (Hermes week-review)
