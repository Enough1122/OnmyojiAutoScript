> AI code review — automated review for reference; please use your judgment.

Correct fix with the failure mechanism documented inline (edge proxy 524s ahead of the 35s poll): the international endpoint gets a 10s ceiling, the CN endpoint keeps 35s, and — the part most fixes miss — server-suggested `longpolling_timeout_ms` is clamped by `min(suggested, max_timeout_ms)` so the server can't push the poll back over the edge limit next cycle. All three behaviors are tested including the suggestion-clamp loop.

— reviewer-b (automated review)

No blocking issues found.
