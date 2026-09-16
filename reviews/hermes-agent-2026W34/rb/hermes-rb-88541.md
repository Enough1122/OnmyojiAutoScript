> AI code review — automated review for reference; please use your judgment.

Precisely gated recovery: the predicate requires *all* of codex_responses mode, the OAuth-provider set, a literal 401, an already-attempted auth refresh, replay still enabled, a token_expired signature, and cached reasoning present — so generic 401s never lose their replay cache and the classifier test pins that 401-token_expired stays `FailoverReason.auth` rather than being quietly reclassified into the replay bucket. Reusing `invalid_encrypted_content_retry_attempted` as the one-shot latch is elegant: a later genuine 400 rejection in the same attempt can't double-strip, and the test proves the second recovery call is a no-op even with fresh cache planted. The suite's "must fail on origin/main" framing is exactly the right regression discipline.

No blocking issues found.

Nit: `_is_codex_token_expired_signature` substring-matches `"token_expired"` anywhere in `str(error)` — a provider message like "refresh token_expired_grace window" would match spuriously. The surrounding gates make this near-harmless today, but anchoring to `token_expired` plus the body-code check (which you already prefer) would keep the signature from widening silently.

— Reviewed by Hermes AI reviewer (reviewer-f2)
