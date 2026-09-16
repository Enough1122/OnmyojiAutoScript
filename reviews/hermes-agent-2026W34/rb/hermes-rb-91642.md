> AI code review — automated review for reference; please use your judgment.

Good defense-in-depth: the guard lives in `selectFamily` *and* at the click site, so no path can silently commit an unavailable model, and the tests cover both the credential-missing and tier-locked shapes including sibling selectability. Items:

- apps/desktop/src/app/shell/model-catalog-menu.tsx:452 — issue (verification) — `disabled` on `DropdownMenuSubTrigger` depends on the Radix version supporting that prop for *sub*triggers; on versions where it's ignored the row stays clickable/hoverable — why it matters — the visual greying would then lie (row looks inert but opens the edit submenu on hover, whose writes are only stopped because they route through `selectFamily`) — suggestion — confirm against the pinned Radix version, add `pointer-events-none` to the unavailable className as belt-and-braces, and pin it with one hover-opens-nothing test.

- apps/desktop/src/app/shell/model-catalog-menu.tsx:196 — issue — the unavailability predicate (`authenticated === false` + `unavailable_models?.includes`) is now duplicated between `selectFamily` and the row renderer — why it matters — when a third signal arrives (e.g., quota-exhausted), updating one copy and not the other produces rows that look selectable but refuse to commit, exactly the confusion this PR fixes — suggestion — extract `isModelUnavailable(provider, familyId): boolean` next to `selectFamily` and call it from both sites.

- apps/desktop/src/app/shell/model-catalog-menu.tsx:479 — issue (UX) — provider-unavailable rows surface the backend `warning` string, but tier-locked rows show only a lock icon with no explanation of *why* or what unlocks them — why it matters — "greyed with a padlock" reads as a bug to most users; the backend presumably knows the gating tier/reason — suggestion — render an optional `unavailable_reasons[family.id]` (or reuse warning) next to the lock when present, even as plain tertiary text like the provider case does.

- apps/desktop/src/app/shell/model-catalog-menu.test.tsx:109 — issue (coverage) — untested paths: keyboard commit (Enter/Space) on an unavailable row, the hover edit submenu staying closed, and the `authenticated === undefined` default-available semantics — why it matters — the keyboard path bypasses `onClick` entirely and is guarded only by the shared predicate, so it's the first thing to break if item 2's helper drifts — suggestion — add the three cases; they're each ~5 lines against the existing harness.

No blocking issues found — this is polish around an otherwise correct and well-tested change.

— reviewer-b (automated review)
