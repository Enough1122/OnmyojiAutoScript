> AI code review — automated review for reference; please use your judgment.

Clean boot-seed design with the right hygiene: localStorage is explicitly a pre-warm (live store wins at runtime), rehydration validates against the same minimal bar `applyTheme` tolerates, built-ins/`default` are excluded in both persist and rehydrate directions, writes happen only on actual change, and the vitest suite simulates real cold starts via `vi.resetModules()` rather than poking internals. Points:

1. apps/desktop/src/themes/backend-sync.ts:~30 — nothing ever *expires* a persisted skin: if the backend stops sending `neon`, the stale entry still rehydrates forever and (via `listAllThemes`) keeps appearing as a selectable ghost theme that may no longer exist server-side. Consider pruning on the first authoritative sync after gateway connect (drop seeds not present in that sync's payload), or documenting the manual-clear path (`resetBackendSkinSync`) as the only removal.
2. Same file — `readPersistedBackendSkins` silently returns `{}` on JSON.parse failure; a single corrupted write permanently disables persistence with zero signal. A one-line `console.warn` inside that catch would make "my skins stopped surviving reload" diagnosable. (nit)
3. Confirm `__resetBackendSkinSync`` is test-only: any production caller (e.g., a future logout flow) would now also wipe the user's persisted skins via the added `removeItem`. If that's desired for logout, fine — just make it explicit in the function's docstring since the name doesn't say so. (nit)
4. The change-detection via JSON.stringify comparison before persisting pairs nicely with the no-rewrite test — good attention to storage churn. (positive)

No blocking issues found.
