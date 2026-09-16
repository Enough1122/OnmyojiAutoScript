> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Correct fix for a real accounting bug: physical session rows rotate at compression boundaries, so the reconstructed agent's in-memory counters under-reported lifetime totals on every /context after a restart or rotation. Making compression counts and token totals durable per row, aggregating them strictly along the canonical compression lineage (branches/delegates/resets deliberately excluded, each pinned by its own test), preferring durable numbers whenever they exist, and recording the externally-owned Codex boundary through the same ledger are all the right calls. The state-layer tests are exactly what this needed - success/failure symmetry for both commit shapes, per-segment-once lineage summation, reset-scope isolation - and the gateway tests cover durable-preferred, fallback-to-resident, and no-resident-at-all.

Two things to confirm:

- **hermes_state_common.py adds the column to SCHEMA_SQL, but where is the migration for pre-existing state.db files?** Every UPDATE touching successful_compression_count fails on an upgraded database unless something ALTERs the column in (reconcile-columns style). If reconciliation is generic, please add the same kind of idempotent-migration regression test the kanban PR carries; if not, this needs an explicit migrate step before merge - as written, the first /context or compaction on an existing install would raise.

- **agent/codex_runtime.py ~309 - the class-attribute probe on type(session_db) works for a plain SessionDB; confirm the async wrapper used on gateway-owned sessions either exposes the method or is never the object seen here**, so the count is not silently skipped for one surface.

Nit: get_compression_lineage_totals recomputes total_tokens from components rather than trusting any stored total - good call; one comment saying billing-total parity is intentional would stop someone from fixing it later.

No blocking issues found.