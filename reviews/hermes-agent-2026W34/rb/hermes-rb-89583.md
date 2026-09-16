> AI code review — automated review for reference; please use your judgment.

Clean catalog entry: URL-only hosted transport (no local spawn), `auth: none` stated plainly, a minimal `default_enabled` surface (`search_tee_times` only), and a post_install note that correctly bounds the capability ("returns links; cannot book/hold/pay") so agents don't promise checkout. Points:

1. Privacy posture worth surfacing to users pre-install: tee-time searches inherently leak location + schedule preferences to pinseeker.xyz. If the manifest schema has an optional homepage/privacy field, populating it would let the install UI show that; otherwise consider a line in the description. (nit)
2. `suggest.hosts` includes golfnow.com — sensible trigger surface; just confirming the suggestion matcher treats these as hints rather than auto-install triggers. Out of this diff's scope either way. (nit)
3. No pinned version/hash for the remote endpoint — the catalog trusts the live service's current behavior. Consistent with other URL-only entries presumably; flagging only so it's a known property of the catalog model. (nit)

No blocking issues found.
