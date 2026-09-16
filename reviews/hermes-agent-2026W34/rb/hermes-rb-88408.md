> AI code review — automated review for reference; please use your judgment.

Solid durable-idempotency design: `(scope, key)` reservations inserted under BEGIN IMMEDIATE make multi-worker admission actually exclusive, fingerprints compared with `hmac.compare_digest`, retention is enforced lazily, WAL is applied with a labeled fallback, file permissions are tightened to 0600 including -wal/-shm, and request bodies/secrets are deliberately excluded from storage. Tests cover both lifecycle branches. Two growth concerns:

1. gateway/platforms/api_server.py:~1551 — `self._run_idempotency_ids` and `_run_owners` grow once per keyed run and are never pruned, even though the *store's* 24h retention deletes rows underneath them. On a long-lived gateway this is a slow memory leak plus stale ownership claims for runs whose rows aged out (`owns_run` then disagrees with the set). Mirror the store's retention: prune these structures on the same cadence or derive membership from a store query.
2. api_server.py:_set_run_status (~6697) — every status transition (including per-tool-event updates arriving through the SSE callback) now issues an UPDATE+commit against the idempotency DB. High-frequency tool events turn this into per-event fsyncs; consider persisting only terminal/relevant transitions and keeping intermediate states in memory, since replay consumers only need the final row after completion anyway.
3. The `:memory:` fallback silently converts durable idempotency into best-effort with no operator signal — one WARNING naming the reason (unwritable path) would explain otherwise-puzzling duplicate-run reports after a restart. (nit)
4. Fingerprint mismatch returning "conflict" (presumably 409) rather than replaying the other body's result is exactly right. (positive)
5. nit: `RunIdempotencyStore.close()` exists but I don't see it wired into adapter shutdown — long-lived WAL connections should be closed on teardown. (nit)

No blocking issues found beyond items 1–2's long-uptime profile.
