> AI code review — automated review for reference; please use your judgment.

Right fix, right diagnosis: the killer detail is that the server-side compression timeout is *floored at 300s*, so the old 120s client budget didn't merely time out — it abandoned an RPC whose server side was guaranteed to keep working for at least another 3 minutes (#83087/#88988). 600s restores the invariant that the client waits out the server instead of racing it, the comment records the reasoning with the cross-references future maintainers will need, and all four affected test expectations were updated together rather than leaving one stale.

No blocking issues found.

Nit: `SESSION_COMPRESS_TIMEOUT_MS = 600_000` now silently encodes knowledge of the server's `_COMPRESSION_TIMEOUT_FLOOR_SECONDS`; when someone raises that floor again, this constant rots exactly as 120s did. Worth either importing the value across the boundary if the gateway exposes it (config or a capability probe), or at least adding "keep ≥ 2× the server compression floor" next to the existing comment so the coupling is written down where the next editor will see it.

— Reviewed by Hermes AI reviewer (reviewer-f2)
