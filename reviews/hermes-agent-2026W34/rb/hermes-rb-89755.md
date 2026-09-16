> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Exactly the right hook semantics for an audit surface: `agent:commentary` fires from a done-callback on the actual send future, so consumers see only text the platform **confirmed** delivered (`success` checked, failures and exceptions silently skipped), carrying the precise delivered string plus the platform's `message_id`. The cross-thread dance is handled correctly too — the done-callback re-schedules the async emit onto `ctx._loop_for_step` rather than awaiting from the wrong loop. The integration test pins the full payload shape field-for-field, which is what a hook contract needs.
