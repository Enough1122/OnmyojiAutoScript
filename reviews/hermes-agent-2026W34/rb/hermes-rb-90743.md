> AI code review — automated review for reference; please use your judgment.

Review of "feat(api): return caller-managed history from runs". Right shape for an allowlist-based boundary: `_RUN_HISTORY_MESSAGE_FIELDS` keeps tool-call linkage and reasoning carriers across resubmit while private persistence/cache markers never leave the server, `include: ["conversation_history"]` follows OpenAI conventions with strict validation, and mirroring compaction/session-rotation into `_compressed` prevents callers from unknowingly resubmitting pre-compaction history. Suggestions:

1. gateway/platforms/api_server.py:6980 (public underscore field) — `r["_compressed"] = True` puts an underscore-prefixed key into a PUBLIC API response dict; underscore conventionally means private, and clients in strict languages will model it awkwardly — expose it as `compressed` at the response layer (keep the internal marker separate) or document the exception.

2. gateway/platforms/api_server.py:1383 (allowlist lifecycle) — the field tuple is the contract for what survives a return→resubmit round trip; add one pinning test asserting an INTERNAL marker key injected into history is stripped from responses, plus a comment telling future provider-integration authors where to register new reasoning carriers — otherwise the next carrier silently gets dropped and resubmits degrade subtly.

3. gateway/platforms/api_server.py:6777 (content=None acceptance) — input entries previously coerced content to str unconditionally; now None passes through (needed for assistant tool-call rows), but confirm every accepted provider path tolerates null content on USER-role rows too, since the validation only checks presence, not type pairing.

4. gateway/platforms/api_server.py:6736 (nit) — unknown `include` values are silently ignored; harmless for OpenAI compatibility, but a debug log listing ignored values would save integrators debugging sessions when they misspell `conversation_history`.

No blocking issues found.
