> AI code review — automated review; please use your judgment.

1. `hermes_cli/web_server.py` (`_apply_model_assignment_sync`) — the old `save_config(cfg)` presumably also persisted assignments for **scopes other than "main"** that flow through this sync; the replacement writes only the top-level `model` map plus the Nous-managed gateway leaves — why it matters: if any caller invokes this with a non-main scope (per-profile model assignment?), its persistence silently disappears under the new targeted writer — suggestion: confirm the function is main-scope-only (add an assert/comment) or extend `_persist_model` to route scoped assignments to their own subtrees; one test per existing scope would pin it.

2. Nit (`utils.py:~623–676`): `_atomic_roundtrip_yaml_mutate_unlocked` duplicates the mkstemp/fsync/owner-mode-restore choreography already present in `atomic_roundtrip_yaml_save`'s internals — factoring a shared ````_rt_dump_atomic(path, yaml_rt, config)```` would keep locking/permission fixes from needing two edits.

3. Nit (`web_server.py`): the `managed_gateway_keys` mapping table encodes knowledge about what `apply_nous_managed_defaults` may touch; when that function grows a section, this table must be edited in lockstep — add a cross-reference comment pointing at its definition (or derive the allowlist from its return value, which the code already tracks via gateway_tools).

The core fix is right and well-tested: replacing the normalized-snapshot `save_config()` with an in-place ruamel round-trip preserves user comments and unrelated keys (#89184), the Nous-managed leaf subset is deliberately re-applied onto the live document, managed installs still refuse writes, and owner-only permissions are restored after persisting an API key — each covered by focused tests including the unicode-personality canary.

— reviewer-a · automated agent review (Hermes week-review)
