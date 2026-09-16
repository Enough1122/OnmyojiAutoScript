> AI code review — automated review for reference; please use your judgment.

This is careful work: the generation-counter (`directoryRequest`) correctly supersedes the old boolean `active` so replaced lookups can't clobber fresh state (three tests exercise exactly those races, including the "initial read resolves after fuzzy typing started" case), `planFolderQuery` cleanly separates browse-path from filter segment with Windows-drive/UNC/~ awareness carried through `clean`/`parentDir`/`pathCrumbs`, the failed-candidate fallback (read parent, keep the last segment as filter) is precisely the right UX, and the combobox/listbox ARIA wiring plus `aria-live` states are better than most pickers ship. Locale keys added across all six translation files including the type contract.

No blocking issues found.

Nits worth a follow-up pass:
1. `remote-picker.tsx:~283` — the 120ms debounce is a bare literal; hoist it next to `_DEFAULT`-style constants so future tuning isn't a hunt.
2. `~330–334` — on fallback, `setPathQuery(queryCandidatePath(typed, currentPath))` recomputes what the closure already computed as `candidatePath` above; reuse the variable (they're equal today, but the duplication invites divergence if normalization changes).
3. `fuzzyScore`'s subsequence match is greedy-leftmost, so scrambled abbreviations ("ha" for "agent-harness") can miss even when an in-order subsequence exists elsewhere; acceptable for a picker, but worth a code comment stating the trade-off so nobody "fixes" it accidentally.

— reviewer-a · automated agent review (Hermes week-review)
