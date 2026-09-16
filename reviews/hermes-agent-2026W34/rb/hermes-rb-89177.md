> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct isolation semantics with the failure mode chosen deliberately: under multiplexing, an explicitly routed profile resolves its own snapshotted personality, and a *missing or empty* snapshot returns `""` instead of falling through to the default profile's prompt — failing closed to "no personality" beats silently speaking with another profile's identity, and the test names that contract explicitly (`test_missing_profile_snapshot_fails_closed`). Precedence stays sane (channel override wins), the active profile is seeded into the map at startup, and all four branches including empty-doesn't-leak are pinned by tests.
