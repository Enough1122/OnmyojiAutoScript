> AI code review — automated review for reference; please use your judgment.

Review of "fix: repair Hermes diagnostics and test tooling". The doctor half fixes a real false positive: SessionDB deliberately RETAINS a ~64MiB WAL high-water for reuse, so the flat 50MB threshold reported an intentional allocation that `--fix` could never clear. `_wal_size_is_runaway` reading the CONFIGURED limit (+1MiB frame slack, floored at the old 50MB) keeps the check meaningful against future limit changes. Suggestions:

1. hermes_cli/doctor.py:_wal_size_is_runaway (nit, coupling) — the function imports `_WAL_SIZE_LIMIT_BYTES` from hermes_state by private name; a rename there silently drops to the 64MiB fallback with no signal — consider exposing it as a public constant or asserting the import in a unit test.

2. Scope note — the PR bundles the doctor fix, a large package-lock regeneration (postcss/sanitize-html bumps), and test tooling changes; splitting would keep the doctor fix independently revertible.

No blocking issues found.
