> AI code review — automated review for reference; please use your judgment.

Correct diagnosis and minimal fix: `is_file()` follows the link and lies about a dangling shim, so checking `is_symlink()` first routes the partial-update case into the heal path instead of silently falling through to whatever `npm` happens to be on PATH. The test builds a real dangling symlink, proves the heal fires, and asserts the *managed* shim wins afterward — covering the regression from both directions.

— reviewer-b (automated review)

No blocking issues found.
