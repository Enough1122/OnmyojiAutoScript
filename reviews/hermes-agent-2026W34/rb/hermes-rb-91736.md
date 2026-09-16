> AI code review — automated review for reference; please use your judgment.

1. `.github/workflows/tests.yml:262–305` — the `coverage` job re-runs the *entire* non-integration suite from scratch after the existing matrix jobs just ran it, roughly doubling CI compute and wall time for every push — why it matters: at 3215 tests this is the most expensive job in the file, and the 40-minute timeout suggests you already expect it to be slow — suggestion: either fold `--cov` into an existing matrix leg, or add `pytest-xdist` (`-n auto`) to this job so the second full pass isn't strictly serial.

2. `pyproject.toml:483–491` — `[tool.coverage.run]` measures lines only; `branch = true` is absent — why it matters: line coverage marks an `if` body as covered even when the error branch never executes, which is exactly the "large untested regression" class HA-D10 wants to catch (untested exception paths are invisible today) — suggestion: enable branch coverage now while the baseline is being established, since enabling it later will move the number and force a re-negotiated threshold.

3. `.github/workflows/tests.yml:296–301` — the gate is global-average only: a PR can add 500 fully-uncovered lines and pass as long as overall stays ≥70% — why it matters: the stated goal ("catch large untested regressions") is precisely what a global average fails to catch at steady state — suggestion: keep 70% as the floor but add a per-diff check (e.g., `diff-cover --compare-branch origin/main --fail-under 90`) as the actual PR gate.

4. `pyproject.toml:487` (`parallel = true`) — nothing in this setup spawns coverage-measured subprocesses, so parallel-mode data suffixing buys nothing and only complicates any manual `coverage combine` debugging — suggestion: drop it unless subprocess coverage is planned.

Nit (`:309`): `continue-on-error: true` on the artifact upload means a broken artifact pipeline fails silently for weeks; consider letting it fail loudly — the gate result is already computed by then.

Overall: long-overdue enforcement mechanism, cleanly wired through `fail_under` rather than magic numbers in YAML; no blocking issues found — items 1–3 decide whether this gate actually bites.

— reviewer-a · automated agent review (Hermes week-review)
