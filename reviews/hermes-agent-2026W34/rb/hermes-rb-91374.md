> AI code review — automated review for reference; please use your judgment.

1. hermes_cli/update_cmd.py:231 — `_maybe_migrate_config_on_current(print_completion)` never uses its `print_completion` parameter (the body only calls builtin `print`). Why it matters: both call sites pass `_print_update_completion`, implying output routing that doesn't happen — under `--quiet`/gateway-mode wrappers this function still writes straight to stdout. Suggestion: either drop the parameter or actually route the informational lines through it, consistent with how the rest of the repair path reports.

2. scripts/desktop-update/posix.sh:541 — the skip detection greps stdout for the literal banner "CODE UPDATE SKIPPED". Why it matters: any rewording of the Python-side banner silently disables the fast-path (degrading to one wasted retry — benign but confusing), and the contract lives nowhere shared. Suggestion: have `hermes update` exit with a dedicated code for the parked-branch skip and match on that instead of prose.

3. scripts/desktop-update/posix.sh:546 — `FINAL_CODE=8` / `FINAL_MSG=…` are assigned immediately before `exit 8`. Why it matters: unless an EXIT trap consumes those variables for status publishing, they're dead stores and whatever reports the desktop-update outcome never learns the skip reason (only the raw code). Verify the trap/publish path handles code 8 distinctly; if not, call `publish_stage`/`log` before exiting (the log line exists — make sure the user-visible status surface gets it too).

4. Parity check: only `posix.sh` teaches the retry loop about the skip. If a Windows sibling (`scripts/desktop-update/*.ps1`) implements the same retry-on-nonzero logic, it will still burn a retry on every parked-branch checkout. Suggestion: mirror the early-exit there.

5. tests/hermes_cli/test_update_config_migration_on.py — nit: new file ends without a trailing newline.

Good test coverage on the Python side: behind/current/ahead versions, warning re-surfacing (#86656), and check-failure silence are all pinned.
