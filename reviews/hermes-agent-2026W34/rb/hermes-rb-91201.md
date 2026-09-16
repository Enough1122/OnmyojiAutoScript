> AI code review — automated review for reference; please use your judgment.

Right call on the asymmetry: the read-only version check proceeds with a warning, while the mutating migration refuses outright rather than running against stale schema code — that matches the blast radius of each path, and #90945's silent-skip failure mode is now at least visible. Points:

1. hermes_cli/update_cmd.py:`_run_config_check_fresh` (~220) — when `failed` is non-empty the function still returns `(current_ver, latest_ver)` from the STALE module. If the caller's flow is "if current == latest: skip migrate", the stale comparison can still conclude *current* and the migration is never attempted — leaving the printed warning as the ONLY signal, quite possibly directly followed by a contradictory "✓ Configuration is up to date" line from the caller. Consider having this function also report the reload-failure condition (tuple element, exception, or a small result object) so the caller can suppress the success claim and/or force the migration attempt.
2. `_run_migrate_config_fresh` now returns `{"skipped": True, "reason": ...}` — verify every consumer of migration results treats unknown shapes benignly (e.g., anything doing `result["migrated"]` would KeyError). A shared TypedDict/literal for the two shapes would prevent future misuse.
3. update_cmd.py — the two ⚠-print blocks are near-identical; extracting `_print_reload_failure_warning(failed, *, migration_skipped: bool)` keeps the wording from drifting between the check and migrate paths. (nit)
4. tests — good coverage of both failure and success branches per function. One gap: no test that the *caller* (update flow) suppresses its success messaging when the skip sentinel is returned — which is exactly the seam item 1/2 worry about. (nit)

No blocking issues found.
