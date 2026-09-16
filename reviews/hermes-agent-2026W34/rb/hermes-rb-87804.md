> AI code review — automated review; please use your judgment.

Clean refactor-plus-feature: `buildProfileGroups` is extracted into its own module (deduplicating the recents-view grouping logic) and reused so messaging platform sections can render per-profile sub-groups aligned with the same keying, colors, and default-first ordering as the recents view. The gate (`showAllProfiles && grouping === 'profile'`) keeps scoped sidebars unchanged, the useMemo dependency list was correctly extended, and the extraction is covered by five focused unit tests including legacy no-profile rows mapping to default and color override/caseless behavior.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
