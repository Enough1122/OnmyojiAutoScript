> AI code review — automated review for reference; please use your judgment.

Correct and minimal: a second Ctrl+C during the bounded memory drain raises `KeyboardInterrupt` (a `BaseException`) straight through the `except Exception` arm and turns shutdown into a traceback; catching it explicitly lets the already-started cleanup finish, and the regression test proves the subsequent provider shutdown still runs.

— reviewer-b (automated review)

No blocking issues found.
