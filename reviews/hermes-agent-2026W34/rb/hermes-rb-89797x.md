> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right parity fix: the fallback chain now mirrors the primary path's `_detect_api_mode_for_url()` mapping for Kimi's `/coding` host, so a working-as-primary provider stops 404-ing (`resource_not_found_error`) the moment it's used as a fallback — and the comment documents the exact wire behavior for the next reader. Findings below are minor:

1. agent/chat_completion_helpers.py:2626 — `"/coding" in fb_base_url.rstrip("/").lower()` is an unanchored substring, so a hypothetical `.../api/codingfuzz/v1` path would also flip to Anthropic Messages. Anchoring to a path segment (parse with urlsplit and compare the first path component against {"coding"}) keeps the special case as narrow as the primary detection it mirrors.
