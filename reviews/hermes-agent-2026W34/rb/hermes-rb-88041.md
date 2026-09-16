> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix for the manual stop/restart path: descendant processes (MCP stdio watchdog + server pairs) are reparented the instant the gateway exits, so snapshotting them **before** `SIGTERM` — exactly mirroring what gateway/run.py's `--replace` path already did — is the only way they remain reapable afterwards. The regression test asserts the full event ordering (snapshot → kill → reap with the snapshotted set and correct parent pid), which pins the subtle part of this fix rather than just its outcome.
