> AI code review — automated review for reference; please use your judgment.

Verified independently before signing off:
- New integrity `sha512-DTg4MJbGMW…F6+w==` matches the published `nanoid@3.3.18` tarball on the npm registry.
- Main-branch `package-lock.json` contains four nanoid copies: root `6.0.0`, `@assistant-ui/react` nested `5.1.16`, plus the two vulnerable 3.x copies (`sanitize-html`, `vite`) — **both** 3.3.17 instances are the ones this PR bumps, so nothing stale is left behind on the 3.x line.
- Parent ranges (`^3.3.16`) accept 3.3.18, so no `package.json` change is required.

No blocking issues found.

Nit: consider adding a top-level `overrides: { "nanoid": "^3.3.18" }` (or `overrides.nanoid@3`) so any future 3.x transitive copy resolves to the patched line instead of relying on each parent's dedup boundary — this also permanently closes the alert that osv-scanner triage (#91737) deferred pending this exact bump.

— reviewer-a · automated agent review (Hermes week-review)
