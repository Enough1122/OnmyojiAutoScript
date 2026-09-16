> AI code review — automated review for reference; please use your judgment.

Right unification: background-process notifications kept a stale SIGTERM-only check while the foreground path had gained the full `_interpret_signal_exit` table, so OOM-killed or segfaulting background jobs reached the model with an unexplained bare exit code. Delegating to the shared table (with the lazy import documented against the real circular dependency), handling both int and numeric-string producers, and the test matrix — OOM via -9 and shell-convention 137, string-form -11, SIGTERM regression guard, clean/ordinary/placeholder negatives — are all correct. Points:

1. tools/process_registry.py:_background_exit_signal_note (~2878) — ```exit_code.lstrip("-").isdigit()``` admits malformed inputs like "--9": lstrip removes *all* leading dashes so the digit check passes, then `int("--9")` raises ValueError that this function does not catch — crashing notification formatting for that event. Tighten to a full-match regex (`^-?\d+$`) or wrap the int conversion; one-line fix.
2. The note line is inserted inside the `[IMPORTANT: …]` block before "Command:" — good placement so the explanation travels with the payload. (positive)
3. Consider asserting once that `_interpret_signal_exit`'s table covers the shell-convention 128+N range generally, since producers may report either convention per signal — the tests sample two signals but the contract is "any lethal signal". (nit)

No blocking issues found beyond item 1's tiny parse gap.
