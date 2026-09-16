> AI code review - automated review for reference; please use your judgment.

Reviewed the visible portion of the diff (the lifecycle-guard pattern changes, capability handshake, and identity-env plumbing; ~42KB of terminal-layer approval wiring and tests not shown here). The security design is unusually careful for a "make a dangerous thing possible" PR: the blanket hard guard is *tightened* to match `--profile` flags so self-targeting cannot bypass by spelling the current profile; the only sanctioned cross-profile shape is exactly five tokens (`hermes --profile NAME gateway restart|stop`) with everything else failing closed; and the sink verifies an HMAC capability binding origin, target, action, nonce, and a <=120s expiry before honoring anything. Re-asserting _HERMES_GATEWAY/_HERMES_GATEWAY_PROFILE/_HERMES_GATEWAY_HOME after dotenv load is an important touch - routing identity must never be dotenv-owned.

- **Capability replay within the window.** The HMAC check validates expiry but nothing consumes the nonce, so the identical approved command re-run inside 120s passes again without a fresh approval. Given env vars are process-local this may be acceptable, but if the terminal layer intends one-approval-per-action, the sink should record consumed nonces (even in-process) - worth stating either way.

- Nit: `_GATEWAY_LIFECYCLE_CAPABILITY_VARS` tuples of env names are read into a dict then indexed by literal strings twice; a tiny dataclass would keep the field list and its uses from drifting.

No blocking issues found.