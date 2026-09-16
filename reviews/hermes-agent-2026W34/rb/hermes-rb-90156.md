> AI code review — automated review for reference; please use your judgment.

Correct fix for a nasty cross-profile bug: writing the emptied state into the *active* store created a shadowing `providers.xai-oauth` stub that permanently hid the root grant from that lane — quarantining into the source store (via the existing `_load_provider_state_with_source` / `_persist_provider_state_to_store` / `_same_path` helpers, all confirmed present on main) restores write-locality, and the test asserts both halves of the invariant (root quarantined, profile stub absent). Points:

1. hermes_cli/auth.py:~5163 — when `_q_source is None` (grant found in neither store), the else-branch still writes an emptied stub into the **active** store. For a grant that never existed this manufactures a `providers.xai-oauth` entry where there was none — mild pollution of exactly the kind this PR removes. Consider returning early (nothing to quarantine) when source is None and `_q_state` is empty.
2. The except-wrapped block means a persistence failure logs at debug and resolution continues raising the original AuthError — right call (quarantine is best-effort), unchanged by this PR. No action; noting I checked. (positive)
3. tests/test_xai_quarantine_source_store.py — strong cross-profile coverage. One addition worth having: the same-path regression case (grant lives in the ACTIVE store → quarantine lands there, no root write), which pins the else-branch you must keep working. If pre-existing tests already cover it, a pointer comment suffices. (nit)
4. Style: the 2026-08-17 dated comment is good archaeology; consider also naming #74339's failure mode in one clause ("shadowing stub hides root grant") directly at the branch rather than only in prose. (nit)

No blocking issues found.
