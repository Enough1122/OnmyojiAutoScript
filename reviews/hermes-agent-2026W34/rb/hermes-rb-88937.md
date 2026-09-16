> AI code review — automated review; please use your judgment.

Correct minimal fix: `resumeStdin()` now drains buffered stdin *before* re-attaching the stored `readable` listeners, mirroring what `unmount()` already does — so keystrokes that arrived while the external editor owned stdin (the submit Enter, stray keys) can't replay through the re-attached listener and re-trigger handlers N times. The comment cites the exact failure mode and the sibling drain site, the fake-stdin test harness simulates the full suspend→buffer→resume sequence and asserts both the drain (`read` called) and the no-replay guarantee (`listener` not called), and the non-TTY early-return path is covered too.

No blocking issues found.

Nit: the new test file is missing a trailing newline at EOF.

— reviewer-a · automated agent review (Hermes week-review)
