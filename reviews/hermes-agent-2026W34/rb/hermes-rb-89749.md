> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right fix shape with the right guardrail: widening to the `glm-5.` family stops each new chat-ID pin from becoming a 3-retry tombstone, while deliberately *excluding* `glm-5v*` — with the comment and a test explaining why (different entitlement; a vision-endpoint 429 must not trigger the shared-key long-backoff class). The test covers bare and provider-prefixed ids plus the old 5.2 regression case.

Nit (non-blocking): agent/retry_utils.py:159 — `"glm-5." in model_name` will also match hypothetical lookalikes (`tglm-5.1`, `aglm-5.x`) inside a longer id string; a cheap tightening is `re.search(r"(?:^|[/:])glm-5\.\d", model_name)` so the family match is boundary-anchored the same way the exclusion effectively is.
