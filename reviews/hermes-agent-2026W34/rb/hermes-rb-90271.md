> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: updater-handoff.log is opened in append mode and never rotated, so years of updates accumulate an unbounded transcript in HERMES_HOME/logs. A size cap (truncate when > a few MB before opening) or a dated suffix would keep the evidence without the growth. Everything else is exactly right: the fd is shared between stdout/stderr so interleaving survives, the parent closes its copy after the detached child inherits it, log-open failures degrade to 'ignore' instead of blocking an update, the stale .update_exit_code marker is cleared before every hand-off so it can only ever describe THIS run, and the new immediateCleanExitIsSuccess flag fixes the silent no-op (direct spawn exiting 0 in-window) while defaulting to true so existing wrapper callers keep their contract — with tests pinning both sides of that distinction plus the degrade-to-ignore path.

— Reviewed by Hermes AI reviewer (reviewer-f)
