> AI code review — automated review for reference; please use your judgment.

Clean change following the established `defaultCollapsed` seed-once contract, and the tests were properly migrated instead of left asserting the old default. Two suggestions:

1. apps/desktop/src/app/skills/embedded-hub-picker.tsx:82 — the seed checks `$paneState(HUB_PANE_ID).get() === undefined` at mount. That's only safe if the panes store hydrates its persisted state synchronously before the first component mount; if hydration is ever async (or reordered), a returning user who deliberately expanded the hub gets silently re-collapsed by the seed. Worth a confirming comment or an assertion that the store is hydrated-before-render — this is exactly the class of bug the "user's own choice always wins" contract exists to prevent.
2. tests — missing the complementary case: mount with a pre-seeded `$paneStates` entry (e.g. height override 400) and assert the seed does NOT fire. The current tests cover never-touched → collapsed and click → opens, but nothing pins "existing preference wins", which is the riskiest half of the change.

3. embedded-hub-picker.tsx:79 — this seed-once stanza is now duplicated per pane (same shape as DetailPane). A tiny `seedPaneDefault(paneId, collapsedHeight)` helper in the panes store would keep the contract in one place. (nit)

No blocking issues found.
