> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): scope display and approvals by topic". Well-layered change: `resolve_display_setting` gains a documented five-level resolution order (chat:thread → chat → parent → platform → global → defaults), the EphemeralReply TTL becomes a first-class display setting with sane clamping (0-3600) while preserving the historical permanent-message default, `_unwrap_ephemeral` threads event.source at EVERY call site (easy to miss one), and the test matrix covers topic-override isolation from DMs, both fallback hops, malformed-policy resilience, and scoped context overrides. Suggestions:

1. gateway/display_config.py:205 (numeric YAML keys never match) — lookup builds `f"{chat_id}:{thread_id}"` STRING keys, but YAML parses a bare numeric chat id (`123456789:` or `123456789:`) as an INT dictionary key, so `platform_channels.get("123456789")` misses and channel overrides silently never apply for exactly the platforms (Telegram/Slack numeric ids) that need them most — coerce `platform_channels` keys via str() during lookup (or document mandatory quoting loudly).

2. gateway/display_config.py:_normalise (nit, silent clamp) — values above 3600 are clamped without any log; an operator setting 7200 gets 3600 with no signal — debug-log the clamp so misconfiguration is discoverable.

3. docs nit — the five-level precedence is valuable enough to deserve a table in the display-config user docs (this diff touches code + tests only), since mispredicting which level wins is the main way users get surprised here.
