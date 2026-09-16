> AI code review — automated review for reference; please use your judgment.

All three gaps are real and the fixes are directionally right: the http/https allowlist fail-closes config-scheme abuse, html.escape plus a deny-all CSP closes the reflected-XSS loopback hole, and the malformed `expires_at` guard stops a TypeError from crashing `get_tokens`. One behavioral consequence deserves a deliberate decision:

1. tools/mcp_oauth.py:`get_tokens` (~509) — after swallowing the bad `expires_at`, the token loads with `expires_in = None`. Pre-fix, the TypeError meant get_tokens blew up and callers treated it as "no valid token" → refresh. Post-fix, whether that stale (possibly long-expired) token gets used depends entirely on how the MCP SDK interprets `expires_in=None`; if None reads as "no known expiry", you can end up *using* an expired access token until an API 401 forces recovery. Safer semantic: treat an unparsable `expires_at` as corrupt-token (return None → refresh flow), not corrupt-field (load without TTL). At minimum, verify and document the SDK's None handling in the comment.
2. mcp_oauth.py:`_resolve_redirect_uri` (~1646) — the ValueError helpfully echoes the configured value; since this can surface through CLI/config errors verbatim it's fine, but make sure no caller turns it into a 500 body elsewhere. No action if CLI-only.
3. `_render_callback_error_page` — consider truncating the reflected `error` to a sane length (e.g. 200 chars) before escaping: authorization servers have been known to echo large query payloads, and the loopback tab rendering megabytes of escaped text is pure noise. Security-wise already sound. (nit)
4. Tests — excellent shape: each gap has both reject and healthy-path cases (numeric `expires_at` still reconstructs TTL within bounds). Missing only a case where `expires_at` is a bool/`true` (JSON truthy non-number) — same branch as "soon", so low value. (nit)

No blocking issues found beyond confirming item 1's SDK semantics.
