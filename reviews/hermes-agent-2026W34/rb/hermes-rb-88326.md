> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Fixes a genuinely confusing signal: for packaged apps, `git rev-parse HEAD` in the update checkout describes the *staging* tree, not what the user is actually running — so a freshly installed client could look arbitrarily behind. Re-basing currentSha on the validated install-stamp commit (40-hex, all-zero rejected), then deriving the rev-list range, changelog selection, and shallow ancestry checks from that running sha is exactly right, and dev checkouts keep live-HEAD semantics. The temp-git-repo test proves the stale-checkout divergence concretely (packaged sha between checkout and origin), and the unusable-stamp fallback matrix covers null/malformed/zero stamps.

Nit (non-blocking): apps/desktop/electron/update-count.ts:resolveRunningClientSha — the 40-hex/all-zero stamp validation duplicates the identical regex+zero-guard just added in about-version.ts (#88665). Extract one `isValidInstallCommit(sha)` helper so both surfaces validate identically and future stamp formats (short shas, tags) get one upgrade.
