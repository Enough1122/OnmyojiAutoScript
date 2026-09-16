> AI code review — automated review; please use your judgment.

Correct root-cause fix, and the diagnosis is precise: persistence stores the resolved *billing class* ("custom"), which is unroutable identity-wise, so resumed ACP sessions silently fell back to `OPENROUTER_API_KEY` against the stored custom base_url. Recovering ````custom:<name>```` from the durable facts (billing_base_url + model) via `canonical_custom_identity` — which I verified exists on `main` — is the right seam, the guard fires only for the literal bare-"custom" case (named pins pass through untouched), and failures degrade to the previous behavior with a debug log rather than breaking restore.

No blocking issues found.

Nit (`acp_adapter/session.py:~558–562`): two small follow-ups — (a) when `canonical_custom_identity` returns None (base_url changed or no matching entry), the code quietly resumes with unroutable `"custom"` and every turn 401s again; a single `logger.warning("could not recover named custom identity for session %s; resumed turns may fail auth", session_id)` would make that state self-diagnosing; (b) add the negative-path test (helper returns None → requested_provider stays "custom") alongside the happy path.

— reviewer-a · automated agent review (Hermes week-review)
