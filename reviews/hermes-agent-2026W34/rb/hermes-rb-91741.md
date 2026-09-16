> AI code review — automated review for reference; please use your judgment.

1. `hermes_cli/plugins.py:~2400–2440` — the fix removes every automatic teardown path for dashboard-auth providers: routine per-home unloads can no longer dispose them (intended), but **nothing else does either** — plugin disable/uninstall and force re-discovery that *drops* a provider entirely leave the process-global entry registered until restart — why it matters: an admin disabling a (possibly compromised) auth plugin expects sign-in via that provider to stop; instead it stays live process-wide (#91701's inverse problem) — suggestion: wire `_ownership_ledger` disposal into the plugin disable/uninstall flow, and have discovery diff evict global providers whose plugin no longer supplies them.

2. `tests/hermes_cli/test_dashboard_auth_plugin_hook.py` — coverage gap around the documented pairing: there is no test that disposing the **current** handle (`unregister_global_provider` identity match → removal) actually empties the registry, nor that a disabled plugin's provider disappears once item 1's wiring exists — why it matters: the identity-conditional logic has four branches and only the stale-dispose branch is tested — suggestion: add (a) current-handle dispose removes provider, (b) double-dispose is idempotent, (c) post-rotation new-handle dispose succeeds.

3. `hermes_cli/plugins.py:~3510` (`_track_registration`) — each forced re-discovery appends another persistent `PluginRegistration` to `_ownership_ledger[plugin_key]` while the superseded one lingers as "active" attribution — why it matters: long-running servers that re-discover periodically grow the ledger monotonically, and `hermes plugins`-style attribution shows stale duplicates — suggestion: replace-in-place for same `(kind, key)` persistent rows, or document the growth as bounded by re-discovery frequency.

4. `hermes_cli/dashboard_auth/registry.py:~126` — `register_global_provider`'s docstring promises upsert-on-name, but there's no warning/log when it *replaces* a different plugin's provider object — why it matters: two plugins claiming the same provider name now silently last-write-wins process-wide, which is harder to debug than the old scoped collision — suggestion: log at WARNING when the existing occupant comes from a different `manifest.name` (pass the owner through `_track`).

Nit: the new tests reach into five private attributes (`_auth_registry._providers`, `_scoped_providers`, `manager._registration_order`, `_ownership_ledger`); a tiny `registry.get_global(name)` helper would keep the regression tests honest against internal refactors.

Overall: right fix for #91701 — moving host-owned infra out of per-home teardown with identity-conditional disposal is sound, and the regression tests capture the original failure precisely. Item 1 deserves a follow-up decision before this ships.

— reviewer-a · automated agent review (Hermes week-review)
