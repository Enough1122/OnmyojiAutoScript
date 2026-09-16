> AI code review — automated review for reference; please use your judgment.

Excellent incident-grade fix: the `os.kill(pid, 0)` → `CTRL_C_EVENT` console-group hazard is precisely diagnosed (including the `BaseException` bypass of `except Exception`), delegated to the repository's cross-platform `_pid_exists`, and the footgun scanner's blind spot that let both bugs live is closed with tests that would have caught them. The AST-based detector instead of a grep is a particularly good call given the explanatory docstrings.

- scripts/check-windows-footguns.py:762 — nit — the new AST rule only matches a *literal* `0` as the signal argument (`node.args[1].value == 0`); a future ``os.kill(pid, signal.CTRL_C_EVENT)`` or an aliased zero constant sails through — worth a follow-up rule matching the attribute name too, since on Windows that spelling is equally lethal.

No blocking issues found.

— reviewer-b (automated review)
