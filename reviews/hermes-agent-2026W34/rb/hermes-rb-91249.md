> AI code review — automated review for reference; please use your judgment.

Correct fix for the double-speak (#90297): the guard sits after the mode/auto-TTS gate and before any `return True`, so it covers every qualifying path, and the tests pin all three mode combinations. Suggestions:

1. gateway/run.py:21976 — the skip is completely silent, unlike every other exit in `_should_send_voice_reply` which logs "Auto voice reply skipped: ...". Add the same log line (with reason="desktop surface speaks locally") so a user who enabled `/voice all` on desktop and hears nothing isn't left debugging a mystery.
2. gateway/run.py:21976 — explicit per-chat `/voice all` is now silently ignored on desktop: there is no remaining way to get a gateway-synthesized reply on that surface even when the client hook is disabled. If that's intended, document it next to the voice-mode command help; otherwise consider keying the skip off the desktop hook being active instead of the platform alone.
3. gateway/run.py:21976 — magic string `"desktop"` is compared here and re-spelled in three test places plus wherever the session routing layer produces it. Promote a shared constant (or a real `Platform` member) so a future case drift (`"Desktop"`, `"desktop-app"`) can't silently disable the guard.
4. tests/gateway/test_desktop_no_gateway_voice_reply.py:18 — `from types import SimpleNamespace  # noqa: F401 (docstring reference only)` is dead code; imports don't serve docstrings. Drop it.
5. tests/gateway/test_desktop_no_gateway_voice_reply.py:24 — `_DesktopPlatform(str)` with `.value` returning `self` is a clever stand-in; since the stated root cause is that the value comes from the session routing layer, importing/borrowing that layer's own factory would keep the stub honest if the runtime shape ever changes. Acceptable as-is with the docstring rationale. (nit)

No blocking issues found.
