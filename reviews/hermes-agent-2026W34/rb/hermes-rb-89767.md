> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right-sized fix: service-managed gateways routinely run with a shim-only PATH, and appending just the missing `os.defpath` baselines — operator entries first, no reordering, no login shell required — restores the system utilities the shim bootstrap (`realpath`/`dirname`) needs without touching anything the operator configured. POSIX-gated correctly, dedup keeps the variable clean, and the order-preservation test pins the important property. Findings below are minor:

1. tests/hermes_cli/test_kanban_db.py — add the degenerate branch to the table: `_merge_worker_path("", defaults)` should return exactly `defaults` (and stay stable on a second merge), since an *empty* service PATH is the most common real-world shape this fix targets and is currently untested.
