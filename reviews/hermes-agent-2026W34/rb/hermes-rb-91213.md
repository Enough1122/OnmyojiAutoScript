> AI code review — automated review for reference; please use your judgment.

Clean sectioning of the roster with the right details done properly: independent per-section pin/recency ordering preserved, search force-reveals both sections, disclosure state survives restarts via plugin storage with a generation guard so a slow hydration read can't clobber a newer click, and the a11y wiring (aria-expanded/controls, counted aria-labels, live-region no-match state) is above average. Minor points:

1. apps/desktop/src/plugins/hermes-bots/plugin.js (`setRosterSectionOpen`) — disclosure state is written to storage on every click but never re-read except at boot, so two windows of the same profile drift apart until reload (last-boot writer's snapshot wins at startup). Fine for now; worth a comment acknowledging the single-window assumption, or a storage listen hook if the SDK offers one.
2. plugin.js (`rosterSectionIsOpen`) — clearing a search snaps both sections back to their saved collapsed state instantly. Consider animating or at least being consistent about whether "search reveals" should stick until the user manually collapses; current behavior is defensible but will feel abrupt to someone who collapsed Groups last session. Product call, not a defect.
3. plugin.js (`RosterSection`) — the attention badge hardcodes a fallback accent (`bg-(--ui-accent,#4f9cf9)`) while every other class here uses theme tokens without fallbacks. If `--ui-accent` is guaranteed elsewhere, drop the literal so theming stays single-sourced. (nit)
4. plugin.js (`beginRosterSectionHydration`) — the name suggests some transaction begins, but it only reads a counter; `currentRosterSectionGeneration()` would describe it honestly and make the hydrate-guard contract easier to follow. (nit)
5. tests/roster-groups.test.mjs — good coverage of the open/close/search-reveal predicate and updated source contracts, but nothing exercises the rendered collapse path (`hidden` attr, disabled toggle during search) since the vm harness can't render. Acceptable given harness limits; the e2e suite is where that belongs if Bot Mode has one. (nit)

No blocking issues found.
