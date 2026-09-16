> AI code review — automated review for reference; please use your judgment.

Clean, complete plumbing of stable gateway route identity to every plugin surface that needs it: private-copied `_gateway_session_source` at agent init (mutation-isolation asserted with `is not` checks throughout), per-message refresh on cached agents so sender changes don't stick, both middleware paths and lifecycle hooks carrying `session_key` + `source`, delegate children inheriting the parent's route, and all three doc references updated including the explicit "not added to model-visible arguments or provider bodies" contract. One privacy note:

- website/docs/user-guide/features/hooks.md:1182 — nit (privacy documentation) — `source` exposes `user_id`/`chat_id` on *every* tool-middleware observation, not just the pre-existing privileged `pre_gateway_dispatch`; plugins that only observe tools now learn who is chatting — why it matters — worth one sentence in the docs stating these are routing identifiers (no message content) so plugin authors make informed choices, and so a future redaction policy has an anchor point.

No blocking issues found.

— reviewer-b (automated review)
