> AI code review — automated review for reference; please use your judgment.

Sound fix for #79005: the success contract is now "active **on an open socket**", the failed-dial path deliberately keeps the active *key* retargeted (so `ensureActiveGatewayOpen` retries the right entry) while leaving socket state honest, and the UI-facing guard in `profile.ts` stops treating a non-null-but-closed socket as already-active. I audited all production call sites — the two `use-gateway-boot.ts` calls are fire-and-forget, the `store/gateway.ts:697` await ignores the result, and only the swap flow consumes the boolean — so the signature change breaks nobody. Test updates across six suites flip the old expectations with rationale comments rather than silently rewriting them, and the new non-null-closed guard test pins the exact reported symptom.

No blocking issues found.

Nit: the comment at apps/desktop/src/store/profile.ts:335 ("only mark the profile active when its socket actually opened") understates what happened — `ensureGatewayForProfile`'s failed path still calls `applyActive(...)`, so `$activeGatewayProfile` *was* retargeted before the boolean said no; what the outer skip actually prevents is the duplicate set plus the `$connection` resync against a dead dial. Worth rewording to "skip the connection resync; the active key was already retargeted by ensure* to drive retry" — the current wording implies the atom wasn't touched, which will mislead whoever debugs the next dual-writer race around this atom.

— Reviewed by Hermes AI reviewer (reviewer-f2)
