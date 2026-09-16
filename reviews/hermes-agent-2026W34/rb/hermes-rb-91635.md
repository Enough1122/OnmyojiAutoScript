> AI code review — automated review for reference; please use your judgment.

Sensible resolution of the footgun: making the ceiling opt-in (`0.0` = absent unless explicitly set) means the implicit default can no longer fight the large-context scaling policy, and the new parametrized test pins all five interesting combinations including strict mode and the disabled-watchdog case.

- agent/chat_completion_helpers.py:1575 — issue (docs/ops) — flipping the effective default from a 120 s cap to "no independent cap" changes operator-visible behavior silently; anything that documents `HERMES_CODEX_TTFB_MAX_SECONDS` as "defaults to 120" (env-var docs, troubleshooting guides, the config reference) is now wrong, and nobody reading logs after an upgrade will know why hangs last longer — suggestion — sweep the docs for the variable name and add a line to release notes stating the new default and how to restore the old ceiling.

- tests/agent/test_codex_ttfb_watchdog.py:151 — nit (coverage) — the malformed-value and negative-value env paths aren't pinned (`HERMES_CODEX_TTFB_MAX_SECONDS=abc` / `=-5`) — worth one parametrized row asserting both degrade to "no cap" rather than raising inside request setup, since this now sits on the hot path for every large call.

No blocking issues found.

— reviewer-b (automated review)
