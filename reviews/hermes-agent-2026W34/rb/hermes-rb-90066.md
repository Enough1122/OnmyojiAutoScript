> AI code review — automated review; please use your judgment.

Correct root-cause fix with the right mechanism: `launchctl submit` jobs are inferred KeepAlive, so the old trailing `launchctl remove` was skipped whenever launchd terminated the helper — leaving a dead-but-respawning label behind per reload. Installing cleanup as an `EXIT` trap *before any work*, plus ````trap 'exit 1' HUP INT TERM```` so handled signals route through that trap, closes every orderly exit path; the doc addition turns the lesson into guidance for external wrappers too.

No blocking issues found.

Nit (`hermes_cli/gateway.py:~4796–4798`): `trap 'exit 1' HUP INT TERM` means a signal landing in the window between `bootout` and `bootstrap` now leaves the gateway fully stopped (old job removed, new one never registered) with only the log line as a trace — no worse than the old default-kill behavior, but since this script is the recovery path it's worth one comment acknowledging that gap, and possibly re-signalling the parent runner so the failed reload is retried rather than silently dropped.

— reviewer-a · automated agent review (Hermes week-review)
