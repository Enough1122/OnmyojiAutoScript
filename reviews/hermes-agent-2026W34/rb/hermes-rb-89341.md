> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Right semantics for a soft-hide feature: archiving hides a chat from lists but never routes delivery away, so an actively-used conversation disappearing forever was a trap. The implementation keeps the blast radius tight - gated on non-internal events only (cron deliveries, background completions, and startup replays cannot drag a deliberately-hidden chat back), placed inside _handle_message_with_agent so it only ever runs for already-authorized inbound traffic, idempotent on concurrent messages, and fully defensive around the async DB door. Tests cover the helper matrix plus both wiring polarities (a user message unarchives; an internal event leaves the flag alone).

No blocking issues found.