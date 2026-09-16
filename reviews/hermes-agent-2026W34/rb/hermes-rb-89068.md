> AI code review — automated review for reference; please use your judgment.

Review of "fix(gateway): force source.profile override in secondary profile handlers". Correct ownership model for multiplex mode: the adapter that received the update owns the credential/profile, and the Telegram shared-user-chat_id case (two per-agent bots, one private chat) shows why a route-derived `source.profile` must never win over the receiving adapter's. The stale-override scenario is tested for all three handler factories. Suggestions:

1. gateway/run.py:15365 (design confirm) — the old `if not event.source.profile` preserved any DELIBERATELY pre-set profile (e.g., a cross-profile forward or routing handoff that pinned the destination); unconditional clobbering removes that escape hatch for every platform in multiplex mode, not just Telegram DMs — worth confirming no such producer exists today, or documenting that receiving-adapter-wins is now absolute.

2. nit — all three handlers still wrap the (now authoritative) stamp in bare `except Exception: pass`; a swallowed assignment failure silently reintroduces exactly the cross-bot leak this fixes — log at debug with the target profile so a broken source object is visible.
