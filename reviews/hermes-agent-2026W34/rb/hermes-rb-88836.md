> AI code review — automated review for reference; please use your judgment.

Sound Windows-specific design: since the updater itself maps executables from the live venv, renaming the directory can never succeed — repointing `pyvenv.cfg` atomically (same-dir temp + fsync + `os.replace`) is the correct primitive, and the failure matrix is handled carefully: smoke-failure rolls the config back, a *failed rollback* preserves the candidate generation (`runtime_generation_in_use`) so the caller doesn't delete the only runtime the live venv now references, and successful cutover cleans the candidate while keeping the generation. Native-Windows tests cover cutover-under-mapped-interpreter, rollback, and the full repair wiring. One nit:

- hermes_cli/managed_uv.py:1003 — nit — `_smoke_candidate_venv(live)` is invoked *after* the config flip, so the name reads oddly (it's smoking the live venv now backed by the candidate); a rename to `_smoke_runtime_at` or a comment stating the deliberate post-cutover smoke would save the next reader a double-take.

No blocking issues found.
