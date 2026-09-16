> AI code review — automated review for reference; please use your judgment.

Well-scoped: OAuth bearers carrying the SuperGrok entitlement belong on the proxy origin where that quota lives, the origin allowlist extension keeps the bearer-leak protection intact (`*.grok.com` added, third-party still rejected, http still rejected — tested), header injection is strictly origin-scoped with add-only semantics mirroring the Copilot guard, and both injection sites are covered. Points:

1. Coverage parity check — #90162 just taught us these identity/header sets must survive *every* client construction path: `_create_openai_client` and `create_openai_client` are covered here, but `_to_async_client` rebuilds `default_headers` from scratch for known hosts and would drop the Grok proxy headers on any aux/vision call routed through the proxy (the same gap that PR fixed for Codex). Please either add the `_is*-host` branch there or route it through a shared `_apply`-style helper.
2. auth.py:~4910 — `x-grok-client-version: "1.0.5"` will rot the moment xAI raises the CLI minimum (the comment says as much). Since the failure mode is a hard 426 across all OAuth users until a Hermes release ships, consider an env/config override (`XAI_GROK_CLIENT_VERSION`) so ops can bump it same-day.
3. The default base-url flip is a behavior change for existing xai-oauth users: silent migration from api.x.ai's free/API tier onto SuperGrok subscription quota. The reasoning in the comment is sound (OAuth == subscription), but this belongs in the changelog, and the pre-existing env override is the documented escape hatch — worth saying so explicitly in the PR body.
4. auth.py:~4907 — the leak-protection warning now lists three accepted origins; the message is getting long. Consider `_XAI_ALLOWED_ORIGINS_DESC` constant shared by validation and docs. (nit)
5. Tests pin origin-scoping thoroughly including the bare `grok.com` near-miss. A companion asserting the *aux* factory injects on proxy URLs would close the loop with item 1. (nit)

No blocking issues found beyond confirming item 1's async path.
