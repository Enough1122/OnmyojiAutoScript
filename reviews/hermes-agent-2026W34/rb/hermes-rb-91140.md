> AI code review — automated review for reference; please use your judgment.

1. `gateway/run.py:~17182–17187` — the early gate passes `event.get_command_args()` **un-lowercased**, while the allow-set (````{"join", "channel", "leave"}````) is lowercase and `gateway/slash_commands.py` lowercases before its own identical check — why it matters: ````/VoIcE JOIN```` slips past the pre-hook gate (hooks/observers fire) and is only denied later by the handler's inner gate, defeating this PR's stated ordering guarantee for uppercase input — suggestion: normalize once (`args = (args or "").strip().lower()` inside the helper, which both call sites already feed raw).

2. `plugins/platforms/discord/adapter.py:~1160–1165` — `... is True` means *any* non-boolean disables VC, including the string `"true"` that a YAML author plausibly writes — why it matters: fail-closed is the right bias, but silent coercion of an intent-to-enable into disabled is a support ticket generator — suggestion: keep the strict check but `logger.warning` when the raw value was truthy-but-not-True, naming the config key.

3. Nit: the ````{"join", "channel", "leave"}```` vocabulary now lives in two modules (`run.py` gate + `slash_commands.py` gate); hoisting it next to `Platform.DISCORD` usage (or onto the adapter as a class constant) keeps future subcommands from diverging between the two gates.

Otherwise excellent: message-voice modes (on/tts/off/status) deliberately stay available when VC participation is off — verified per-mode including side-effect-free assertions on save/join mocks — the resolver-unavailable path fails closed with a warning, explicit `null` survives seeding specifically so the adapter's fail-closed validation sees it, native slash autocomplete drops VC choices when disabled, and the denial-before-hooks ordering has a dedicated regression test using the real dispatch pipeline.

— reviewer-a · automated agent review (Hermes week-review)
