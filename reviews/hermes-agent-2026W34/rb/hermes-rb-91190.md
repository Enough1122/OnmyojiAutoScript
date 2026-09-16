> AI code review — automated review for reference; please use your judgment.

The distinction drawn here is exactly right: a **raw `<@bot>` token typed inside a quote-reply** is a deliberate invocation (→ new thread), while a mention that materializes only through Discord's automatic reply-ping resolution is ambient context (→ stays inline). Hoisting `is_reply_message`/`inline_mention` above the display-stripping step is necessary for the raw-token check to see unmodified content, the guard ordering keeps `no_thread_channels` and voice-linked channels winning over the new behavior, and both directions have focused regression tests with honest docstrings.

No blocking issues found.

Nit (`plugins/platforms/discord/adapter.py:~8168–8172`): ````skip_for_reply```` reads as a double negative in the condition (`not skip_for_reply`) and `inline_mention` actually means "raw-token mention within a reply"; renaming to e.g. `reply_without_direct_mention` / `reply_has_raw_mention` would make this branch self-documenting for the next reader.

— reviewer-a · automated agent review (Hermes week-review)
