> AI code review — automated review for reference; please use your judgment.

Review of "fix(tools): keep blank context lines in V4A hunks". Excellent fix for a genuinely dangerous parser bug: dropping interior blank context lines shortened the search pattern, which could re-anchor an edit onto a different block while reporting success — the worst failure mode an edit tool has. The pending-blank buffer is the right shape: interior blanks commit only when a real hunk line follows, trailing runs stay separators, counters reset at every hunk/op boundary, and end-of-patch blanks simply never commit. The wrong-anchor regression test (PRIMARY vs BACKUP) demonstrates the actual harm rather than just the parse delta. One nit:

- whitespace-only lines that still contain spaces ("   ") are NOT caught by `not line` and flow through as context with their trailing spaces intact — consistent with strict V4A semantics, but worth one comment noting that only FULLY empty lines get the blank-context treatment, so nobody extends this branch later and changes anchor behavior for indented producers.

No blocking issues found.
