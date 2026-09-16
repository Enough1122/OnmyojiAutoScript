> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): make hidden cron jobs discoverable in sidebar" (INITIAL_VISIBLE_JOBS 3→6, "x of y" badge, row-style load-more). Solid, well-tested UX fix; findings below are polish/hardening suggestions, nothing blocking:

1. apps/desktop/src/app/chat/sidebar/load-more-row.tsx:18 — `visibleLabel` unconditionally appends a hardcoded '…' to the localized label — if any locale's sidebar.loadCount/loadMore string already ends in an ellipsis (ASCII or fullwidth), the row renders doubled punctuation, and the suffix bypasses translators entirely — normalize before appending (strip a trailing '…') or move the ellipsis into the i18n strings themselves.

2. apps/desktop/src/app/chat/sidebar/cron-jobs-section.tsx:189 — the badge renders `shownOf(shown.length, Math.min(sorted.length, max))` — if `max` ever caps the denominator below the true job count, "6 of N" understates how many jobs stay hidden and contradicts what load-more eventually reveals — worth confirming `max` >= sorted.length on every path (or documenting why capping the denominator is intended).

3. apps/desktop/src/app/chat/sidebar/cron-jobs-section.test.tsx:96 — the new test covers only the expand-once happy path — no assertion that the "6 of 7" badge disappears once hiddenCount reaches 0, and none for the jobs <= INITIAL_VISIBLE_JOBS case where badge and button should never render — adding those two cases locks the boundary behavior this PR is about.

4. apps/desktop/src/app/chat/sidebar/load-more-row.test.tsx:41 — the row variant is tested only in its ready state — the loading branch (`!loading ? `${label}…` : label`, spinner child instead of text) has no coverage, so a future refactor could silently regress the ellipsis suppression — a small loading-state row-variant test would pin it.

5. apps/desktop/src/i18n/types.ts:1580 — the counter lands in cron.shownOf while its sibling affordance strings (loadMore/loadCount/loading) live under sidebar.* — one interaction split across two namespaces invites drift across the five locales touched here — consider colocating them or cross-referencing in comments.

Nice touch reusing SidebarLoadMoreRow with a variant instead of duplicating the affordance.
