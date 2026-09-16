> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Solid upgrade on both axes: the retry path now honors a numeric `Retry-After` verbatim (falling back to the capped exponential backoff for non-numeric/HTTP-date values), and surfacing `usage.server_side_tool_usage_details.x_search_calls` turns the degraded-detection heuristic into ground truth — `x_search_calls == 0` means the index never ran (unsourced prose), while calls>0 with empty citation channels means a genuine no-match. The distinction between those two degraded reasons is exactly what callers need. Tests are exemplary: per-code retryable vs non-retryable matrices, header-honoring sleep assertions, and all three degraded branches.

Nit (non-blocking): tools/x_search_tool.py:385 — the move from `status_code >= 500` to an explicit set quietly *narrows* retries (501 and 505+ are no longer retried where they previously were). Almost certainly correct — 501 Not Implemented isn't transient — but it's a behavior change worth a line in the PR description so nobody reads the new set as purely additive.
