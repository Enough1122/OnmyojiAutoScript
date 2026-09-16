> AI code review — automated review for reference; please use your judgment.

Solid addition — the rationale comments are unusually good, the fail-closed choice on short flags is well argued, and the test file covers positives, negatives, controls, and approval-key distinctness. A few refinements:

- tools/approval.py:1077 — issue — the same uncommitted-work hazard exists via `git switch --discard-changes <branch>` (documented as throwing away local modifications), which this PR leaves uncovered even though `switch` is git's modern replacement for `checkout` — why it matters — an agent told to avoid `checkout -f` will plausibly reach for `switch --discard-changes`, silently bypassing the gate — suggestion — add a parallel pattern (and one positive/negative test each) for `git switch.*(--discard-changes|-f|--force)`.

- tools/approval.py:1077 — issue — the pathspec alternative requires literal `\s--\s`, so spellings where `--` is glued to the next token slip through, e.g. `git checkout --"$f"` or `git checkout --`(pwd)` — why it matters — these are realistic shell-generated forms and they *do* discard working-tree changes — suggestion — match `(?!-)[\s]`+ `--` + lookahead for non-option start (`\s--(?![-\w])`) and add a glued-quoting test case.

- tools/approval.py:1070 — issue — the `--staged` exemption is a raw substring scan (`[^\n;|&`]*--staged`), so a path literally named `--staged` (`git restore -- ./--staged`) suppresses the prompt for the whole segment — why it matters — a crafted or coincidental filename turns a destructive restore into a silent one — suggestion — require the flag to be its own token: `(?:\s)--staged\b` instead of bare `--staged`.

- tests/tools/test_git_worktree_destructive.py:60 — issue (coverage) — nothing pins down how `_normalize_command_for_detection` handles non-ASCII whitespace (NBSP, zero-width joiner) between `git` and `restore`/`checkout` — why it matters — if normalization ever stops folding those, every pattern here silently stops matching and the suite stays green because all fixtures use plain ASCII spaces — suggestion — add one parametrized case using `git\u00a0restore\u0020.` asserting it still detects (or explicitly assert the normalization contract).

No blocking issues found; items 2 and 3 are hardening rather than correctness regressions.

— reviewer-b (automated review)
