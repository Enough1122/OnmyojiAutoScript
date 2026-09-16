> AI code review — automated review for reference; please use your judgment.

Correct shape fix with the AWS union documented inline where future readers need it: non-streaming `ReasoningContentBlock` nests text under `reasoningText`, and the tolerant fallback keeps already-flattened delta blocks working. Tests cover the union member, the flat legacy shape, redacted-only blocks (no phantom text), and full absence — all four outcomes that matter.

— reviewer-b (automated review)

No blocking issues found.
