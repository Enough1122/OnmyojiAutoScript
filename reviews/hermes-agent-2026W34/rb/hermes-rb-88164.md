> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. This is the same `npm run fix` auto-formatting as **#88170 and #88173** (identical connection-config.ts / use-session-tile-delegate.ts / session-states.test.ts changes; this PR carries only the connection-config.ts hunk). That makes three duplicate formatter PRs in this batch - please close two and keep one so the formatting standardization lands once with a single attribution.

(The formatting itself is fine: blank-line normalization, a multi-condition join, and an expect-array reformat - no behavioral content.)