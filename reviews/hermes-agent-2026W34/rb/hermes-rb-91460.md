> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Solid fix overall — the classifier mirrors `_is_session_expired_error`'s bounded identity-visited traversal, the InterruptedError short-circuit protects user interrupts, and the stdio/http integration test proves the rebuild-and-retry plumbing end-to-end. Findings:

1. tools/mcp_tool.py:4986 — the message-marker list (`"connection closed"`, `"connection reset"`, ...) can misclassify application-level failures as transport staleness: a tool whose own backend dies mid-execution often surfaces "connection reset by peer" *after* the operation partially ran. Reconnecting and re-running `tools/call` then executes a possibly non-idempotent tool a second time. Why it matters: duplicate side effects (double POST, double write) are worse than a transient visible error. Suggestion: for `tools/call`, retry only on type-name matches (`RemoteProtocolError` etc.) and keep marker-based matching for the read-only `resources/*` paths — or gate marker-based tool retries behind a per-server idempotency flag.

2. tools/mcp_tool.py:6151 — retry budgets stack across recovery handlers: `_handle_session_expired_and_retry` already re-runs the op once; if *its* retry raises a stale-connection error, the fall-through reaches the new handler for a second reconnect+retry, so a single user call can execute the tool up to three times. Suggestion: thread a shared per-invocation retry budget through the `_call_once` closures and let later handlers respect it.

3. tools/mcp_tool.py:5118 — after a successful reconnect, a retry result that fails `json.loads` is still returned as success and resets the server error counter. An unparseable response is exactly the kind of half-broken state the breaker exists to track. Suggestion: only call `_reset_server_error` when parsing succeeds and no "error" key is present; return the raw string either way if you want to preserve behavior.

4. tools/mcp_tool.py:5106 — the fixed 15s `_signal_reconnect_and_wait` timeout ignores the caller's remaining deadline (tool handlers carry their own timeout, e.g. 10s in the test), so a slow reconnect can turn a 10s tool call into a >25s stall before the generic error path runs. Suggestion: derive the wait timeout from the handler's remaining budget.

Test-gap nit: no negative test asserts that an app-level error merely *containing* a marker phrase (e.g. `RuntimeError("backend connection closed unexpectedly")`) does or doesn't trigger a tools/call retry — whichever way #1 is resolved, pinning it down in tests/tools/test_mcp_stale_connection_retry.py would prevent silent regressions.
