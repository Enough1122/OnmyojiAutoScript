> AI code review — automated review for reference; please use your judgment.

1. **hermes_cli/doctor.py:1139-1142 (module name used as pip spec)** — the hint interpolates the *import* name: `telegram` renders as `…install with: … telegram`, but `telegram` on PyPI is an unrelated abandoned project — the distribution is `python-telegram-bot`. Following this hint installs the wrong package (or nothing useful) and leaves the user worse off than the old bare warning. `discord` happens to work because the `discord` PyPI name aliases discord.py, but that's luck, not correctness. **Why it matters:** this PR exists to make the warning actionable; for one of the three listed packages it isn't. **Suggestion:** carry an explicit pip spec per entry (`("telegram", "python-telegram-bot", "python-telegram-bot")`) exactly as PR #89142 does, so import-name ≠ dist-name can't regress this again.

2. **Overlap with #89142** — this modifies the identical optional-packages hunk (same base blob `a75c9c6c`) as #89142, which already implements the explicit-spec version of the same idea plus a regression test. **Why it matters:** whichever merges second produces a pointless conflict, and right now the repo has two competing shapes for the same fix. **Suggestion:** coordinate in #89121 — land one (preferably the spec-table variant), close/rebase the other against it.

3. **tests/hermes_cli/test_doctor.py:288-306** — the fake-import approach is clean and narrowly scoped, but it pins only the `discord` case — i.e., the one package where the module-as-spec shortcut happens to work. A `telegram` case would fail against today's code, which is exactly what a regression test is for. **Why it matters:** without it, item 1 ships green. **Suggestion:** parametrize over telegram/discord asserting each renders its *distribution* name in the hint.

Nit: consider asserting on the full warning line rather than two independent substrings (`"discord.py (optional, not installed)"` and the hint) so a future reordering of label/suffix can't silently split the message across lines.

— Reviewed by Hermes AI reviewer (reviewer-f2)
