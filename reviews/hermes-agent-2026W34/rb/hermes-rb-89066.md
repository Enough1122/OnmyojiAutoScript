> AI code review — automated review for reference; please use your judgment.

Review of "fix(tui): dismiss overlays on rpc failure". Right unblock: an RPC failure used to leave approval/clarify overlays stuck forever with no way to answer them, and `respondWith` left spinners wedged. Dismissing is strictly better than a dead overlay. Two safety-flavored notes:

1. useInputHandlers.ts (silent deny) — if `approval.respond {choice:'deny'}` fails on a TRANSIENT network error, the overlay now vanishes as if the deny landed, but the gateway never received it and will resolve the dangerous command by its own timeout path; consider surfacing a brief error notice ("deny failed — the request may still be pending") instead of a silent dismissal, since this is the one overlay where the user believes they made a safety-relevant choice.

2. useMainApp.ts `respondWith` — `.catch(() => done())` swallows every failure including genuine errors; callers can't distinguish success from failure and the user gets zero feedback. A shared toast/notice on the catch path (even just the RPC method name) would keep the fix while preserving signal.

No blocking issues found.
