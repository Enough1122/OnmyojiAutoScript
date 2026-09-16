> AI code review — automated review for reference; please use your judgment.

The fix lands at the right point: binding `rememberHeaders` to the **final** profile-scoped URL (post-`registryGatewayWsUrl`) means the CF-Access credentials minted for profile A can never satisfy a WebSocket dial for profile B on the same shared remote — previously the pre-scope URL was remembered while the renderer dialed the scoped one, so exact-match lookups missed and whatever fallback logic sat under `headersForRemoteRequest` decided cross-profile fate. Extracting the store/handler into `remote-ws-headers.ts` with injected dependencies makes the whole thing unit-testable, and the negative matrix is exactly what this class of bug needs: sibling pathname, different `profile`, different `ticket`/`token`, and *reordered* query params must all receive no headers, plus insertion-order eviction preserved and both auth paths (token/OAuth) covered end to end.

No blocking issues found.

Nit: the store's 100-entry cap evicts strictly by insertion order, not recency — a user cycling through many profiles on one remote can evict the entry for the profile they're about to redial, though any dial through the IPC handler re-remembers it, so the failure mode is one extra round-trip rather than breakage. If it ever matters, bumping to an LRU-on-access (`headersFor` re-inserts) is a two-line change; noting it here mainly so the constant's arbitrariness is documented as deliberate.

— Reviewed by Hermes AI reviewer (reviewer-f2)
