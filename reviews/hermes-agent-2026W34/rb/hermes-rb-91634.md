> AI code review — automated review for reference; please use your judgment.

Correct and minimal: slash-command events now carry the same guild identity as the message path, the resolver degrades gracefully through `interaction.guild_id` → `channel.guild.id` → `None` (DMs stay guild-less), and both construction sites are covered.

- tests/gateway/test_discord_slash_commands.py:400 — nit (coverage) — the fallback branch (`guild_id` absent but `channel.guild.id` present) and the DM shape (resolves to `None`) aren't pinned; both are cheap SimpleNamespace cases — worth adding since the fallback is exactly what older discord.py object shapes will exercise.

No blocking issues found.

— reviewer-b (automated review)
