> AI code review — automated review for reference; please use your judgment.

Review of "fix(cron): let scripts tell a scheduled fire from a manual run". Excellent small feature with an unusually clear problem statement: one-shot watchdog scripts that disarm by deleting their state file are non-idempotent, so running one manually silently consumed the pending alert before the intended recipient ever saw it — and nothing in the environment let a script defend itself. `HERMES_CRON_RUN=1` fixes that with minimal surface, the comment preserves the whole failure narrative for future maintainers, and the tests drive REAL scripts through the real runner in both directions including the end-to-end disarm watchdog. One nit:

- website docs — the cron scripting page should document `HERMES_CRON_RUN` alongside any other script-visible env (`HERMES_HOME` etc.), since its whole value depends on script authors knowing it exists.
