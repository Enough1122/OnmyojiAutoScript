> AI code review — automated review for reference; please use your judgment.

Well-scoped fix for #91077: the credential axis is additive, strictly gated on *both* sides carrying a fingerprint (so every existing call site keeps its behavior — pinned by `test_unknown_credential_on_either_side_is_non_distinguishing`), and the error-direction analysis is right: an unresolvable side can only cause an extra harmless rotation attempt, never a wrongly skipped account. Test matrix covers all four interesting combinations. Items:

- agent/backend_identity.py:131 — issue (verification) — `BackendIdentity.build` normalizes the new credential field with `_norm_provider(credential)` — reusing the *provider* normalizer for a credential string — why it matters — if `_norm_provider` ever grows alias mapping or prefix handling (plausible: it exists to canonicalize provider labels), it will silently mangle fingerprints; today it presumably just strips/lowercases, which happens to be safe for `sha:<hex>` — suggestion — use a dedicated trivial `_norm_credential()` (or plain `(value or "").strip()`) so the coupling is gone.

- agent/backend_identity.py:97 — nit — an 8-hex-char fingerprint is 32 bits; fine at realistic scale, but since these now gate identity decisions, spending 12–16 chars costs nothing and pushes birthday-collision territory beyond any conceivable install; a collision here would silently merge two distinct accounts and skip a working fallback.

- agent/chat_completion_helpers.py:2517 — issue (known limitation, worth documenting) — when `agent.api_key` is callable (the Entra ID path noted in the comment) the primary side contributes no fingerprint, so two Entra accounts behind one endpoint still collapse into one deployment and #91077 reproduces for that auth mode — suggestion — either call the resolver in a try/except to obtain the token material for hashing, or add a line to the fallback docs stating per-account pools require static keys today.

No blocking issues found.

— reviewer-b (automated review)
