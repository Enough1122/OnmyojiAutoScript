> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-defined hook contract upgrade: `agent:end` now sees the **full** response (the old 500-char truncation made any transform lossy before it ran) and its mutations are honored with precise edge semantics — string replaces, empty string silences, a *removed* key is a no-op rather than an accidental wipe, and non-string values are ignored with a notice instead of corrupting the send path. The test suite pins every one of those branches including the >500-char end-to-end delivery and the model/provider passthrough. Findings below are minor:

1. gateway/run.py:20166 — the type-mismatch notice uses `print(...)` while everything around it logs through `logger`; on a daemonized gateway that line vanishes into stdout. Use `logger.warning("[hooks] agent:end 'response' must be str, got %s; ignoring mutation", type(_new_response).__name__)` so misbehaving hooks are visible in gateway logs too.
