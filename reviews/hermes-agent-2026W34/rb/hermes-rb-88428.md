> AI code review — automated review for reference; please use your judgment.

The domain layer delivers the plan's core: scope-keyed ownership enforced at read *and* write, NFC+SHA-256 content identity with expected-hash pre-check, terminal-run immutability behind a lifecycle guard, URI canonicalization that strips fragments/credentials and lowercases scheme/host, partial-unique-index dedup instead of service-only checks, and the go/no-go tool gate isolated in its own module so the non-core surface ships separately. The test set covers schema/fresh-upgrade/idempotency plus real multi-connection writer races. Points:

1. research/evidence_fabric.py:`EvidenceFabricService` — every persistence call reaches into SessionDB privates (`_execute_write`, `_lock`, `_conn`). That couples this new domain package to storage internals the plan says it "extends without modifying"; if SessionDB changes its locking or gains a read-retry wrapper, the fabric silently bypasses it. Ask SessionDB for a small public surface (a `transaction()` and `fetchall()`) — the class already exists conceptually as `_read_ctx`.
2. `_fetch` executes directly on `_conn` under `_lock` rather than through the read-context path other readers use; confirm WAL/busy-retry behavior is equivalent, otherwise list calls can raise SQLITE_BUSY where sibling readers wouldn't.
3. `_is_lifecycle_integrity_error` matches trigger RAISE message strings verbatim — stable only because the triggers live in the same schema file; one comment binding them together (or error codes in the RAISE) would keep a message edit from silently breaking conflict classification.
4. Style nit: several dataclasses/enums are packed onto single lines with semicolons, which fights the repo's formatter and makes diffs noisy on the next edit.
5. Process observation (not a defect): the plan+spec documents are ~45% of the diff bytes; fine for this workflow, but the implementation itself is ~175 lines, so reviewers should weight the tests heavily — they're where the real contract lives.

No blocking issues found.
