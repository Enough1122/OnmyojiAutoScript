> AI code review — automated review for reference; please use your judgment.

Right fix for the torn-copy class of bug: the online backup API + post-snapshot `integrity_check` is materially safer than `copyFileSync`, and the WAL-inclusion test is exactly the proof needed. Items:

- apps/desktop/electron/main.ts:3582 — issue (verification) — `preflightStateDb` became async; please confirm there are no remaining fire-and-forget call sites beyond the two updated ones (`applyUpdates`, `applyUpdatesPosixHandoff`) — why it matters — an un-awaited call means the updater spawns while the snapshot is still running, reintroducing precisely the kill-backend-mid-copy race this guards against, now with a false sense of safety — suggestion — grep for `preflightStateDb(` and make the promise chain explicit (avoid `void`), or return a completion token the handoff waits on.

- apps/desktop/electron/sqlite-backup.ts:7 — issue — opening the source strictly `readOnly` can fail with SQLITE_CANTOPEN for a WAL-mode database whose `-shm` sidecar is missing (backend killed mid-checkpoint leaves exactly that shape), and `backup()` can throw SQLITE_BUSY while the still-alive backend sustains write load — why it matters — in both cases the emergency backup silently vanishes, i.e., the update proceeds with *no* safety net where the old dumb copy at least produced something — suggestion — add a bounded retry (2–3 attempts, short delay) for busy errors and a last-resort plain `fs.copyFile` fallback logged loudly as unverified, so the net degrades instead of disappearing.

- apps/desktop/electron/sqlite-backup.ts:22 — issue (perf) — `integrity_check` plus full backup run synchronously in the update hot path; on multi-GB `state.db` files this can add minutes with only the final size log as feedback — why it matters — users read the pause before an update as a hang and kill the app mid-preflight — suggestion — log start/duration (and byte count streamed if available) around the backup, and consider skipping deep verification above a size threshold with an explicit "backup not verified" marker.

- apps/desktop/electron/sqlite-backup.test.ts:14 — issue (coverage) — the failure paths are untested: verification detecting a corrupt snapshot (mock `integrity_check` to return `not ok`) must delete the destination and rethrow, and the partial-file cleanup on backup throw — why it matters — the cleanup logic is what prevents a corrupt `.bak` from being mistaken for a good emergency copy later; it deserves the same pinning as the happy path — suggestion — add the two negative tests with a stubbed `DatabaseSync`.

No blocking issues found — item 1 is a quick verification, items 2–4 are hardening.

— reviewer-b (automated review)
