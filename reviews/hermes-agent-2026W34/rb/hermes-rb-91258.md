> AI code review — automated review for reference; please use your judgment.

Overall this is a well-reasoned change: the pin keeps owning plumbing while the newest real conversation wins, guards are sensible, and the fallback paths are covered by tests. Non-blocking observations:

1. apps/desktop/src/plugins/hermes-bots/plugin.js:3628 — `newerVisibleBotChat` treats an absent `message_count` as real history. Gateways that omit the count even for empty drafts would reintroduce the exact blank-chat case this guard exists to prevent. Consider requiring a secondary signal (`title` or `last_active`) when `count` is unknown.
2. plugin.js:3703 — the bare `catch {}` around `openStoredBotChat(newer)` silently falls back to the pin for every error class (deleted session, IPC failure, hydration timeout). A debug/warn log before falling back preserves the "row never dies" behavior while keeping real breakage visible.
3. plugin.js:5584 — correctness now depends entirely on the caller passing the freshest *visible* session for *this* bot as `latestVisible`. An assertion/filter at the roster source (or a documented contract) would stop a future refactor that passes a cross-bot or hidden row from silently hijacking the click target.
4. plugin.js:3621 — the helper never compares recency itself; it trusts the caller's ordering. If the roster ever sorts by created-time instead of activity, a stale session could win. Comparing `last_active` against the pinned session's (when both exist) would make the guard self-contained.
5. plugin.js:3473/3570/3585 — flipping `keepAllProfilesScope` to `false` changes scope for everything downstream of an open, not just creation (hide sweep, DM delivery, cross-profile lookups). Tests cover open/creation paths; consider one integration-style check that exercises hide-sweep/DM delivery after opening under the new scope.
6. tests/bot-row-opens-latest.test.mjs:14 — the vm slice depends on the `const canonicalCreations` / `function displayName(` source markers; a rename would silently drop all coverage. Acceptable pragmatism, but exporting the helpers would be sturdier. (nit)

No blocking issues found.
