> AI code review — automated review for reference; please use your judgment.

Well-scoped feature reusing upstream config vocabulary (`allow_from` / `groups.<id>.allow_from` mirroring authz_mixin, so one mental model covers both), with the right default semantics (unset/empty adds no denial), independent DM/channel scopes, `*` catch-all, CSV-or-list normalization, and a test matrix covering every combination including the DM-doesn't-narrow-channels asymmetry. Items:

- plugins/platforms/mattermost/adapter.py:933 — nit — denied senders are dropped at debug level only; an operator who typos a user_id in `allow_from` gets silence exactly where they're looking for a response — suggestion — log denials at info (once per sender/channel pair per cooldown) or expose a deny counter in status output.

- plugins/platforms/mattermost/adapter.py:936 — nit (coverage) — no test for the `"*"` catch-all member or a `groups` entry keyed by case-insensitive channel-id match (the lookup supports both); each is two lines against the existing harness.

No blocking issues found.

— reviewer-b (automated review)
