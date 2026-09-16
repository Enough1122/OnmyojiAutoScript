> AI code review — automated review for reference; please use your judgment.

Review of "fix(agent): read auth_token in request_dump so OAuth requests stop showing 'Bearer None'". Right fix in the right place — the fallback sits inside the existing try/except, preserves api_key precedence, keeps the explicit "Bearer None" marker for credential-less clients, and the new tests cover all four quadrants. Minor suggestions:

1. agent/agent_runtime_helpers.py:1890 (debug fidelity) — when BOTH api_key and auth_token are set, the Anthropic SDK can emit X-Api-Key and an Authorization bearer simultaneously, but the dump now reports only the api_key bearer — a reader debugging auth could miss that an OAuth surface is also active — consider emitting a masked secondary entry (or an `also_auth_token: true` flag) when both credentials exist.

2. tests/agent/test_request_dump_auth_token.py:30 (stub drift) — `_StubAgent._mask_api_key_for_logs` re-implements the production masker by hand; if the real masker changes (length thresholds, sentinel strings), these tests keep passing while actual dumps differ — prefer importing the real `Agent._mask_api_key_for_logs` (unit-pure) or asserting against a shared helper so the contract can't silently diverge.

3. tests/agent/test_request_dump_auth_token.py:60 (coverage gap) — no case exercises a CALLABLE `auth_token` through the new fallback branch to produce the documented `<entra-id-bearer>` sentinel — that path is half the motivation for this change (per the code comment), so pinning it with one test would be cheap insurance.

4. agent/agent_runtime_helpers.py:1889 (nit, confirm intent) — `if not api_key:` means an explicitly empty-string `api_key` also falls back to `auth_token`; that seems desirable, but worth confirming it can't mask a misconfigured client where `api_key=""` should surface as an error instead.

No blocking issues found.
