> AI code review — automated review for reference; please use your judgment.

Clean, well-motivated fix (xpcproxy denying log files on external volumes is a real failure mode) and the regression test asserts the right things. Items:

- hermes_cli/gateway.py:4738 — issue — `{log_dir}` is interpolated into raw plist XML without escaping; a Hermes home containing `&`, `<`, or `>` (e.g., `/Volumes/Work & Personal/Hermes`) produces a malformed plist that launchd silently refuses to load — why it matters — this bug predates the PR, but these exact lines are being refactored right now, and ironically external-volume homes (the ones this change targets) are *more* likely to live at user-chosen paths with ampersands — suggestion — build the strings via `xml.sax.saxutils.escape(str(log_dir))` while touching them.

- tests/hermes_cli/test_gateway_service.py:265 — issue (coverage) — only the omission path is pinned; there's no companion assertion that an internal (`~/...`) home still emits `StandardOutPath`/`StandardErrorPath` — why it matters — the cheapest future regression here is dropping redirection for everyone (a one-line condition slip), and nothing would catch it — suggestion — add the mirror-image test asserting both keys are present for a normal home.

- hermes_cli/gateway.py:4734 — nit — `/Volumes` is a hardcoded heuristic: it correctly covers USB/network mounts but not exotic setups (firmlinks, custom mountpoints); worth one comment line stating the assumption, and note that when redirection is omitted launchd discards stdout/stderr entirely — a generated-plist comment (`<!-- app logs: HERMES_HOME/logs -->`) would help whoever debugs that install later.

No blocking issues found — behavior looks correct for the stated problem; items 1–2 make it durable.

— reviewer-b (automated review)
