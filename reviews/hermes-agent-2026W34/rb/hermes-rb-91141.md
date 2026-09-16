> AI code review — automated review for reference; please use your judgment.

Correct layer for the fix: reusing `preserveLocalPendingTurnMessages` (the same identity/ordinal proof the session-resume path already trusts) means stale `sessions.changed` REST reads can no longer delete a turn that just settled over the stream, while rewinds still replace unrelated history. The two tests cover both halves that matter — immediate protection against a lagging read, and eventual convergence onto the durable row once it appears — which is exactly the contract worth pinning.

No blocking issues found.

Nit (`apps/desktop/src/app/contrib/hooks/use-background-sync.ts:~110–122`): if the durable row *never* arrives (backend persistence failure), the locally-completed turn is now grafted on every future refresh indefinitely — better than deletion, but a silent permanent divergence from server history. Consider a soft bound: after N consecutive refreshes still without a matching durable row, log/warn (or surface a subtle "not synced" marker) so users and support can tell ghost-from-authoritative; also worth a one-line comment here naming the shared proof helper as the single source of truth for what counts as "matching".

— reviewer-a · automated agent review (Hermes week-review)
