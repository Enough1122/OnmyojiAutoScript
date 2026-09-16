> AI code review — automated review for reference; please use your judgment.

1. agent/chat_completion_helpers.py:4426 — the new `usage_obj is None` condition assumes usage arrives *only* in a terminal usage-only chunk. Why it matters: several OpenAI-compatible gateways and backends emit a usage object on **every** chunk (or on the last content chunk before an abrupt cut). For those, a genuine mid-stream drop leaves `usage_obj != None` from an earlier chunk, and the stream is now misclassified as cleanly completed — exactly the silent-truncation failure this guard exists to catch, just via the opposite sign. Suggestion: only treat usage as proof of clean close when it was carried by the *final* chunk consumed (track a `usage_in_last_chunk` flag, or require that no content delta followed the chunk that carried usage); alternatively gate the heuristic on providers known to send a terminal usage-only frame.

2. tests/run_agent/test_partial_stream_finish_reason.py:795 — both new tests cover the canonical vLLM shape, but not the adversarial case from item 1 (usage-bearing chunks followed by a severed connection), nor a tool-call stream with a trailing usage chunk (the guard's `not tool_calls_acc` arm). Suggestion: add both — the first pins whichever semantics you choose for item 1.

3. agent/chat_completion_helpers.py:4424 — when usage presence suppresses the drop warning, nothing records why. Suggestion: emit a debug log ("stream ended without finish_reason but with usage; treating as clean close") so future misclassification reports are diagnosable from logs alone.

Nice regression discipline: both sides of the boundary are tested (clean usage-terminated stream vs abrupt drop without usage), with the stub-id and finish_reason contracts asserted explicitly.
