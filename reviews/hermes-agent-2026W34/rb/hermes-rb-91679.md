> AI code review — automated review for reference; please use your judgment.

Nice pair of fixes; the safeStorage/keychain-ACL rationale for ad-hoc signing is well explained, and the self-heal tests cover the important pre-list boot case. Findings:

- apps/desktop/scripts/after-pack.mjs:47 — issue — `codesign --force --deep --sign -` re-signs *everything* in the bundle ad-hoc, including nested helpers/frameworks that may still carry a valid third-party or Developer ID signature when only one broken component caused `--verify` to fail — why it matters — the stated invariant ("a real Developer ID signature is never clobbered") only holds at the top level; a single corrupt nested binary downgrades the whole bundle's identities — suggestion — log the original verify stderr before re-signing, and consider signing the outer bundle without `--deep` so nested signatures are preserved unless individually invalid.

- apps/desktop/scripts/after-pack.mjs:41 — nit — Apple documents `--deep` as a verification aid rather than a signing mechanism; fine for an unsigned local bundle today, but worth a comment noting it may need replacement (`codesign --sign -` per-framework then outer) if Electron's layout changes break it.

- apps/desktop/src/store/profile.ts:196 — issue — `profiles.length === 0` conflates "list not fetched yet" with "fetch succeeded and backend reports zero extra profiles"; in the latter state a stale active profile is never healed because `profileIsKnown` always returns true — why it matters — a user who deletes their last remote profile keeps an app wedged on 404s, which is precisely the bug this PR fixes — suggestion — track fetch completion (e.g., a `$profilesLoaded` boolean set after a successful `refreshProfiles`) and treat "loaded && empty" as authoritative.

- apps/desktop/src/store/profile.ts:344 — issue — only the *active* gateway profile is healed; `$newChatProfile` and any persisted routes/session state referencing the deleted profile are left dangling, so the next-chat picker can still aim requests at a 404-ing name — why it matters — partial reconciliation leaves a second path into the same wedge — suggestion — in `reconcileGatewayProfile`, also null out `$newChatProfile` when it fails `profileIsKnown`, and document that saved routes are handled elsewhere (or handle them).

- apps/desktop/src/store/profile.test.ts:141 — issue (coverage) — there is no test pinning the "successful refresh that returns an empty list" semantics discussed above — why it matters — whichever way item 3 is resolved, the current suite passes either way, so the decision is untested — suggestion — add one test asserting expected behavior when the backend reports zero profiles after a prior non-empty list.

No blocking issues found — items 1 and 3 are the ones most worth addressing before merge.

— reviewer-b (automated review)
