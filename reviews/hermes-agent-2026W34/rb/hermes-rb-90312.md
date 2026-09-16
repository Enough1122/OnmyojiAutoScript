> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

The runner classification itself is well-built: real-file inspection beats directory shape, pytest signals win immediately over remembered unittest signals, plain-assert test functions correctly default to the permissive `python -m pytest`, emitting `python -m <runner>` avoids bare-`pytest` env mismatches, and the test matrix (precedence, root-level tests, empty/no tests dirs, framework recipes) is thorough. Findings:

1. agent/verify/recipes.py:_find_python_test_files — the one-level scan introduces a regression class the old shape-check handled: projects that nest tests (`tests/unit/test_x.py`, `tests/integration/`, or `src/pkg/tests/`) have **no** level-1 test files, so `_python_test_command` returns `[]` and the verify recipe silently drops its test phase entirely — where the old code would at least have run pytest because `tests/` existed. Since a silent no-test verdict is worse than a slightly-wrong runner guess, either deepen discovery (bounded rglob for `test_*.py`/`*_test.py`, e.g. depth ≤3) or keep the old fallback: if `tests/` exists but no level-1 files matched, still emit the pytest command.

2. Scope — tests/tui_gateway/test_log_exit_broken_pipe.py rides in this PR but tests a `_log_exit`/`_sw_log` BrokenPipeError guard that belongs to an unrelated shutdown-noise fix; splitting it out keeps this PR's bisect surface honest (and note the file is missing its trailing newline).
