> AI code review — automated review for reference; please use your judgment.

Review of "feat(api): add reversible session archive endpoints". Clean REST addition: shared `_set_session_archived` core with auth/404/503 handling, both routes registered and advertised in capabilities, idempotent semantics verified by a full archive→unarchive→persisted-state round-trip test plus the unknown-id 404 case. One design note:

1. gateway/platforms/api_server.py:3573 (overlap with PATCH) — `PATCH /api/sessions/{id}` already accepted an `archived` boolean, so there are now two write paths for the same flag; harmless, but document which is canonical for clients (or note that PATCH may be narrowed later) so integrators don't build against both.
