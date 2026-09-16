> AI code review — automated review for reference; please use your judgment.

1. `cron/scheduler.py:~4577` (`_run_cron_conversation`) — when `inspect.signature()` raises `TypeError`/`ValueError`, `accepts_task_id` defaults to **True**, forcing `task_id=` onto agents whose signature couldn't be inspected — why it matters: introspection uncertainty becomes a hard `TypeError` mid-run inside the pool, failing the job instead of degrading gracefully — suggestion: default to `False` (call `run_conversation(prompt)`) when the signature can't be determined, or catch `TypeError` around the `task_id` call and retry without it.

2. `hermes_cli/cron.py:~99` (`_current_cron_inference_defaults`) — any exception while loading config returns `({}, "", "")`, and `cron_list` then compares job snapshots against empty current provider/model — why it matters: a transient config-read failure renders every snapshotted job as `[drift-blocked]` with scary remediation hints, i.e. false alarms precisely when the system is unhealthy — suggestion: return `None` on load failure and skip the drift decoration block entirely (print nothing rather than print wrong things).

3. `cron/scheduler.py:~4536` (`_resolve_cron_terminal_timeout`) — invalid configured values (non-numeric strings, `0`, negatives, floats like `"90.5"`) are silently skipped down the chain to the hidden `180` fallback — why it matters: a typo'd `cron.terminal_timeout` silently reverts long builds to 180s kills with no signal, recreating the exact pain this PR fixes — suggestion: emit a warning naming the offending source key/value, and consider rejecting non-integral numbers instead of quietly ignoring them.

4. `tools/terminal_tool.py:~2604` (`_resolve_command_timeout`) — `config["timeout"]` raises `KeyError` if the key is ever absent, and discarded overrides give no feedback — why it matters: the session override silently loses to a crash-or-silent-fallback pair — suggestion: `config.get("timeout", <module default>)` plus a debug/warn log when an override value fails validation.

5. `hermes_cli/subcommands/cron.py:~117` — `--terminal-timeout` is `type=int`, so there is no CLI way to *clear* a per-job pin (empty string won't parse; omission preserves) — why it matters: users who pin 900s during a migration have no supported undo back to `terminal.timeout` follow-mode — suggestion: accept a sentinel (e.g. `--terminal-timeout none` → stores `null`) or document the manual JSON edit; same story for `config set cron.terminal_timeout`.

6. Test coverage gap — the two riskiest new seams have no direct tests: (a) `run_job` registering and **clearing** the session terminal override (the `finally` cleanup path, incl. the exception-swallowing branch), and (b) `_run_cron_conversation`'s no-`task_id` fallback branch — suggestion: add focused unit tests for both before merging, since regressions here surface only as hung or crashed scheduled jobs.

Nit: `cron/scheduler.py:~4509` — the bare `except Exception: alias = None` in `_resolve_cron_inference_route` swallows genuine config corruption; narrowing to expected errors or adding a `logger.debug(..., exc_info=True)` would keep failures diagnosable.

Overall: well-scoped feature, atomic-route aliasing design is sound, and the docs/tests added are genuinely useful. Items 1–3 deserve attention before merge.

— reviewer-a · automated agent review (Hermes week-review)
