> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right fix — surfacing agent failures instead of dressing them up as \`assistant.completed\` payloads, with clean redaction via \`_redact_api_error_text\` and good dual-endpoint tests. Points:

- **gateway/platforms/api_server.py:~2545-2562 + 3840-3848 — every agent failure becomes \`502\`, which rewrites upstream 4xx classes into retryable ones.** The PR's own test shows \`"HTTP 400: requested model is invalid"\` surfacing as \`status=502 / err_type="server_error"\`. Standard HTTP clients and SDK backoff loops treat 5xx as retryable and 4xx as terminal, so a permanently-invalid model request now gets retried N times before failing — extra latency, duplicated side effects, confusing support reports. Suggestion: when \`raw_error\` matches the apparent \`HTTP <code>:\` convention already visible in these messages, propagate that class (400 stays 400, mapped to an OpenAI-compatible \`invalid_request_error\`); keep 502 for unclassified crashes, and/or emit \`X-Hermes-Upstream-Status\` so callers retain fidelity either way.

- **api_server.py:~2550-2553 — partial-success semantics are implicit and unpinned.** With \`partial=True, completed=True, failed=False\` plus an \`error\` string, the check returns None and the turn reports success while an error sat on the result. That's probably intended (degraded-but-delivered), but nothing tests or documents it; one assert-away test (`test_partial_result_with_error_still_succeeds`) would lock the contract against future tightening of this condition.

- **api_server.py:~2551 — legacy results default to success.** \`bool(result.get("completed", True))\` means any older code path returning dicts without the new keys can never fail here — including the case \`{"final_response": "", "messages": []}\` after a silent internal crash. The new \`_run()\` wrapper sets the keys on exception (good), but empty-`final_response`-without-keys remains indistinguishable from legit empty replies. Worth at least a code comment stating this is deliberate backward-compat.

- **Duplication between the two handlers.** Non-stream builds \`_openai_error(...) ["error"]["hermes"]\`, stream builds an \`_event_payload("error", ...)\` with the same fields; extracting a small \`_agent_failure_payload(failure)\` keeps the wire format from drifting as fields evolve.

- **tests/gateway/test_api_server.py:1057-1120 — coverage nits.** No assertions on the new response headers (\`X-Hermes-Completed: false\`, session-key propagation on the error path), no non-dict-result case for \`_agent_failure_details\`, and the \`_run()\` exception-path change (completed/failed/error injection) has no direct unit test.

Solid regression shape overall — the stream test's negative asserts (no \`assistant.completed\`/\`run.completed\`) are exactly right.
