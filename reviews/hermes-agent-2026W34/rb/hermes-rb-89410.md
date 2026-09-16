> AI code review — automated review for reference; please use your judgment.

Correct and well-tested: Copilot's Anthropic relay validates signed thinking end to end, so exempting it from the third-party strip preserves multi-turn reasoning continuity and satisfies the tool-result replay protocol. Hostname-safe detection is tested against both spoof shapes (path-embedded and suffix-embedded lookalikes), the conversion test pins block order (thinking → text → tool_use) with signatures intact, and the generic-third-party strip is regression-guarded. Updated docstring explains both exceptions in one place.

— reviewer-b (automated review)

No blocking issues found.
