> AI code review — automated review for reference; please use your judgment.

- optional-mcps/mengram/manifest.yaml:34 — Nit: `suggest.keywords` includes the generic word `memory`, whereas existing catalog entries stick to brand-identifying terms (e.g., linear's only keyword is `linear`). Why it matters: the desktop pill may be suggested whenever users type about memory features generally, which reads as an endorsement-shaped upsell rather than a brand match. Suggestion: drop `memory` or replace with something unambiguous like `mengram.io`.

Verified: manifest structure mirrors the approved sibling entries (linear) field-for field including the case-1 native-OAuth auth block; the advertised discovery endpoints respond (both `/.well-known/oauth-*` URLs return 200 and `https://mengram.io/mcp/connector` correctly answers 401 unauthenticated), so the transport/auth claims are accurate as written.

_— hermes-week-review automated review (reviewer-d)_

No blocking issues found.