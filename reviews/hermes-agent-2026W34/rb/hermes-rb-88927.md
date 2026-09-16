> AI code review — automated review; please use your judgment.

Right fix for real log pollution (31% escape bytes in worker logs): gating is centralized in one `_diff_ansi_enabled()` predicate that checks `NO_COLOR` (the standard opt-out) and tty-ness **per call** with the uncached choice explicitly justified, all five color helpers plus a new `_diff_reset()` are gated so reset codes disappear too, and the test matrix covers non-tty, NO_COLOR-on-tty, fake-tty-keeps-color, and content preservation under plain rendering.

No blocking issues found.

Nits:
1. (`agent/display.py` `_diff_ansi_enabled`) consider also honoring `FORCE_COLOR`/`CLICOLOR_FORCE` for users who pipe to a color-aware pager but still want escapes.
2. (`:~97`) the function-local `import sys as _sys` is odd next to module-level imports of `os`; a top-level `import sys` reads cleaner unless there's a circularity worth a comment.

— reviewer-a · automated agent review (Hermes week-review)
