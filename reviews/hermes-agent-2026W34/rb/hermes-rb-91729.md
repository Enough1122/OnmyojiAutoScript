> AI code review — automated review for reference; please use your judgment.

1. `tools/skills_hub.py:~267–270` (`_normalize_lock_install_path`) — the new `source != "official"` depth cap applies whenever `source` is supplied, including **re-recording during update**: an existing grandfathered non-official entry recorded at `a/b/skill` depth under the old validator will raise `ValueError` the next time the hub updates/re-records it — why it matters: legal-yesterday installs become un-updatable today (uninstall still works, per the new test, but that's cold comfort) — suggestion: exempt re-records whose incoming `install_path` exactly matches the entry already in the lock (true grandfathering), or migrate those rows once instead of failing.

2. `tools/skills_sync.py:~615–622` (`_backfill_optional_provenance`) — after switching to `lock.record_install(...)`, the trailing `installed[lock_name] = {"install_path": install_path}` mutates a local dict that is never persisted again (each `record_install` reloads+saves internally), and every backfilled skill triggers a full lock load+serialize+atomic-replace cycle — why it matters: the residue line misleads readers into thinking batch state matters, and N backfills cost N whole-file writes — suggestion: delete the dead assignment; optionally add a `record_installs(batch)` that saves once.

3. `tools/skills_sync.py:~355–374` (`_optional_skill_index`) — the ambiguity policy keeps an alias when it coincides with some skill's *exact install path* (`alias not in exact_paths` guard) but no test covers that branch — why it matters: this precedence rule is precisely what decides whether a user typing the colliding slug gets the right skill or a silent skip, and it's currently regression-unprotected — suggestion: add a case where a folder-name alias equals another skill's install path and assert the exact-path mapping wins.

4. Behavior note (`tools/skills_sync.py:~407`): `restore_official_optional_skill("*")` now deliberately returns "not found" ("all" only). Any script/doc that used `*` breaks quietly with a generic message — worth a line in the PR body/changelog, or teach the error message to say `use 'all'`.

Nit: `_backfill_optional_provenance` calls `is_excluded_skill_path(skill_md)` without `root=` while `_optional_skill_index` passes `root=optional_dir` — unify so both apply the same exclusion semantics regardless of CWD.

Overall: solid hardening follow-up — alias disambiguation, microsecond backup stamps, permission-preserving atomic lock writes, and provenance backfill through the validated writer are all real improvements. Item 1 needs a decision before merge since it strands existing users.

— reviewer-a · automated agent review (Hermes week-review)
