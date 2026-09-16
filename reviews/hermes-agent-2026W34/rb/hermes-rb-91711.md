> AI code review — automated review for reference; please use your judgment.

1. `plugins/platforms/discord/adapter.py:~1160–1170` — suppression defaults **on**, flipping visible behavior for every existing deployment without a config change — why it matters: users who deliberately rely on preview cards (e.g., channels where the bot shares docs links and readers click the cards) lose them silently after upgrade; this belongs in the changelog/release notes as a behavior change, not just a new knob — suggestion: call it out explicitly in the PR body, and consider whether status/notification messages should keep previews while conversational replies suppress them.

2. `plugins/platforms/discord/adapter.py` (whole diff) — the flag rides only the three *text-chunk* send paths (`send`, its no-reference retry, `_edit_overflow_split` continuations); if the adapter has separate media/file send paths (attachment uploads with caption text containing URLs), those still unfurl — why it matters: partial suppression produces inconsistent per-message behavior that reads as a bug — suggestion: grep the adapter for other `channel.send(` / `.add_files(` call sites and either propagate the flag or document why attachments are exempt.

3. `plugins/platforms/discord/adapter.py:~1187–1196` (`_coerce_suppress_link_previews`) — YAML `suppress_link_previews:` with no value arrives as `None`, which falls into `bool(None) → False`, i.e. an *unfilled* key disables the safety-default instead of keeping it — why it matters: every other boolean here treats absent/unset as the documented default; a bare key is much more likely "didn't finish editing the config" than "deliberately off" — suggestion: short-circuit `if value is None: return True` before the bool cast.

4. Nit: the long "content-only edit preserves SUPPRESS_EMBEDS" rationale now lives twice (constructor comment ~1163 and again above `edit_message` ~3816) plus once more in the test module docstring — three copies of a library-version-dependent claim (`discord.py 2.7.1`) that must age together; point two of them at the third (or a single docs anchor) so a future discord.py upgrade updates one place.

Overall: well-executed small feature — correct lever (`suppress_embeds` at send time), honest treatment of the streaming-edit subtlety, config coercion with tests, and complete docs. Items 1–2 are judgment calls worth making consciously before merge.

— reviewer-a · automated agent review (Hermes week-review)
