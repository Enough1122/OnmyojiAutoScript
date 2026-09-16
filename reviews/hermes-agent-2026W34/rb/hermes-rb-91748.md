> AI code review — automated review for reference; please use your judgment.

1. `hermes_cli/web_server.py:5505` — After a restart reconciles from `update.log`, `exit_code` stays `None` even when the durable tail contains the `=== hermes-update completed <id> ===` marker — why it matters: the UI cannot distinguish "completed successfully" from "crashed/never finished", which is the exact ambiguity this PR aims to close — suggestion: parse the completion marker and synthesize a success result (e.g. `exit_code=0`, `running=False`) or expose a `durableCompleted` field the frontend can render distinctly.

2. `hermes_cli/web_server.py:5510` — `durable_tail` replaces `tail` whenever `result is None`, including while the updater is genuinely still running inside the *current* server process (result map not yet populated) — why it matters: the endpoint already reported `running=False` above, and substituting the mirrored log mid-run makes the status endpoint claim a live update is idle — suggestion: gate the fallback on the process being absent too (e.g. `name not in _ACTION_PROCS`) so it only applies post-restart.

3. `apps/desktop/src/store/updates.ts:208` — `maybeNotifyUpdateAvailable` now defaults `target='client'`; any call site missed by this diff silently shifts from the old remote-aware ternary to client-only overlays — why it matters: a missed caller reintroduces the "remote users update the wrong target" bug in one notification path — suggestion: grep all remaining callers of `maybeNotifyUpdateAvailable` and pass `target` explicitly (drop the default) so the compiler forces each site to choose.

4. `hermes_cli/update_cmd.py:1124` — only the `flush()` is guarded; the preceding `print()` of the receipt can itself raise `BrokenPipeError` if the parent is killed between the banner print and the flush — why it matters: the receipt (the whole point of this change) would be lost in precisely the race being fixed — suggestion: put `print(...)` and `sys.stdout.flush()` inside the same try/except, or write the marker to the durable `update.log` mirror directly here.

5. `tests/hermes_cli/test_web_server.py:1282` — the test seeds `hermes-update.log` but the assertion only exercises `update.log`; the extra file is dead setup — why it matters: it implies the endpoint reads that file when it doesn't, misleading future maintainers — suggestion: delete the unused write or add an assertion proving it is intentionally ignored.

Nice-to-have nit: `apps/desktop/src/store/updates.test.ts:94` — the `lastToast()` cast assumes `action` is always present; a non-null assertion helper with a clear failure message would make future toast-shape changes easier to debug.

Overall: solid root-cause analysis (single-target ternary left remote users updating the backend forever) and good test coverage on both sides. Items 1–2 are worth addressing before merge; none are outright blockers in my read.

— reviewer-a · automated agent review (Hermes week-review)
