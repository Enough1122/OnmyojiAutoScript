> AI code review — automated review for reference; please use your judgment.

Exemplary security design end to end. Highlights worth naming: default-off policy requiring *two* explicit opt-ins (`enabled` + `operator_read_only`); exact-name allowlists that reject glob characters by construction; the final pre-transport policy/runtime re-check under the gateway reload lock with a dedicated test proving a mid-flight notification cannot swap the authorized handler (TOCTOU closed); bounded arguments/schemas/results with UTF-8-safe truncation; `_meta.session` OAuth timing metadata stripped from result envelopes; credentials canaried in tests for both logs and returned text; stable numeric RPC error codes mapped from symbolic service errors; profile mismatch rejected before any service lookup; and the desktop capability store validating gateway payloads so strictly that every malformed shape drops to empty. The busy-lock-instead-of-queue choice for concurrent calls is right for an interactive surface. Items:

- tools/mcp_client_access.py:31 — nit — `_client_locks` grows one entry per server name ever seen and is never pruned; trivial memory, but a one-line cleanup when a server disappears from config keeps it tidy.

- apps/desktop/src/store/host-capabilities.ts:104 — nit — `hostCapabilityScope` falls back to profile-only keying when `connectionId` is null; two distinct backend connections sharing one profile name would then read each other's cached descriptors during that window. Confirm connectionId is always set at ingest time in practice, or fold the connection identity into the fallback too.

No blocking issues found — this sets the standard the other client surfaces should follow.

— reviewer-b (automated review)
