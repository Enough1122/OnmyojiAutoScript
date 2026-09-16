> AI code review — automated review for reference; please use your judgment.

Security-conscious feature done right: the new `plugin` media mode validates at *both* ends (renderer-side URL minting and main-process re-parsing), handles nested percent-encoding (`%252e` → `%2e` → traversal caught), rejects fragments/duplicate params/non-allowlisted query keys before any backend resolution, enforces `audio/*|video/*` response types with body cancellation on rejection, keeps tokens out of URLs and out of assistant-authored HTML (the forged-`hermes-media:` source test), scopes profiles correctly for shared vs self-owned backends in both directions, and documents the honest trust boundary ("namespace convenience, not an authorization boundary"). Items:

- apps/desktop/src/api/plugins.ts:23 vs apps/desktop/electron/media-protocol.ts:55 — nit — `assertSafePluginMediaSegment` exists as two copies across renderer and main processes; justified defense-in-depth for a trust boundary, but nothing ties them together — suggestion — add a cross-reference comment on each ("keep in sync with …") so a future relaxation in one flags the other in review.

No blocking issues found.

— reviewer-b (automated review)
