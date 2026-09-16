> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: `profileGroupLabel` re-runs `normalizeProfileKey(profile.name)` for every live profile on every grouped-view rebuild. Irrelevant at realistic profile counts, but if it ever matters, memoize a normalized-key map next to the profiles fetch. The three regression cases (renamed display_name, unset display_name, removed-but-recent profile) are exactly the right table.

— Reviewed by Hermes AI reviewer (reviewer-f)
