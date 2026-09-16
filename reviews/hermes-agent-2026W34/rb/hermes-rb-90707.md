> AI code review — automated review for reference; please use your judgment.

Right fix at the right seam: guarding inside `send()` *after* the HTTP-response and `deliver: log` early-returns keeps programmatic consumers untouched while human-directed routes get an honest notice plus a WARNING that names session and route. The classifier tests (whitespace smuggling, quoted-placeholder pass-through) are exactly right. One structural concern:

1. gateway/platforms/webhook.py:`_TERMINAL_ERROR_PLACEHOLDERS` (~100) — the drift test only proves set ⊆ conversation_loop source; it cannot catch the opposite direction. When someone adds a *new* terminal placeholder upstream ("Incomplete X after 3 retries" for a changed budget), the guard silently stops covering it while all tests stay green. The durable fix is a shared constant module (e.g. `agent/error_placeholders.py`) imported by both conversation_loop.py and this adapter — then the string-matching drift test can be deleted entirely. If `_sanitize_gateway_final_response` in run.py keeps its own copy of these strings, that's already three sites to sync.
2. webhook.py:~407 — the notice embeds `reason` (the raw placeholder) and `route` unescaped into the delivered message. For GitHub-comment delivery the body is markdown — a placeholder containing backticks/underscores would render oddly; harmless today since all six strings are plain prose, but worth remembering if the set grows user-influenced text.
3. webhook.py:~975 — `"route": route_name` is only written at route registration; sessions created before this deploy have no key, so their notice says "(webhook route: ?)". Consider falling back to the chat_id's route segment (`webhook:<route>:<ts>` already encodes it) instead of "?". (nit)
4. The WARNING is good; consider adding `final_response` length or turn id so operators can correlate with the specific run in logs. (nit)

No blocking issues found.
