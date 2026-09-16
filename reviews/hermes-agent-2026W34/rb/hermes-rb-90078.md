> AI code review — automated review; please use your judgment.

Additive and well-constructed: the manifest pins a remote HTTP MCP endpoint with native OAuth 2.1/PKCE (no secrets in-tree, asserted by test), deliberately leaves all 18 tools enabled at install with the pruning trade-off documented against the n8n precedent, and the five skills push mechanics to the server's own `skills/get` workflow so they don't rot as the product evolves — while keeping what only the client knows: approval gating ("only approved posts may be scheduled"), account discovery instead of guessing, read-back verification, and honest status reporting. The HARDLINE tests pin manifest fields, transport/auth shape, no-secret hygiene (`sk-`, `api_key:`, Bearer patterns), required SKILL.md sections, and the known tool vocabulary. Docs pages + catalog reference updated in lockstep. I verified the `post_install` text does contain the ````hermes mcp configure socialrobot```` string its test asserts.

No blocking issues found.

Nit (`optional-mcps/socialrobot/manifest.yaml`): the composer suggestion keyword ````"post-scheduler"```` is generic enough to surface the install pill for unrelated scheduling chatter; the brand-specific ````socialrobot````/````social robot```` plus the host match likely suffice, so consider dropping the generic term.

— reviewer-a · automated agent review (Hermes week-review)
