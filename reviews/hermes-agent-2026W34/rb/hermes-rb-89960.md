> AI code review — automated review for reference; please use your judgment.

Exactly how fail-closed endpoint verification should be built: keyword-only identity parameters keep every zero-arg call site byte-identical (pinned), runtime identity triggers an origin allow-list (provider × api_mode × hostname) with a deny matrix covering spoofed hosts and partial identities, the Anthropic `speed=fast` lane is transport-gated to native Messages, and even the blocking-rework guard for xAI fast-mode support is documented in the test parametrize comment.

— reviewer-b (automated review)

No blocking issues found.
