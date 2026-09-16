> AI code review — automated review; please use your judgment.

Correct fix with the right platform nuance: `shlex.split(editor, posix=(os.name != "nt"))` preserves backslashes in Windows paths while still honoring quotes there, and the regression test exercises a genuine executable path containing a space end-to-end (fake editor script + quoted $EDITOR), not just the tokenizer in isolation.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
