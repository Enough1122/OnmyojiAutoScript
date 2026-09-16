> AI code review — automated review; please use your judgment.

1. `agent/credential_pool.py` (`_sync_codex_entry_from_auth_store`, ~adopt block) — the rewritten `should_adopt` drops the old dedicated branch for **"auth.json has a newer refresh_token but no access_token"**: now `store_access` must be non-empty for any adoption, so a store that was rotated refresh-only (access already consumed elsewhere) is ignored and its single-use refresh grant goes stale/unreplayed — why it matters: the removed comment explicitly said adopting that refresh_token prevented replaying a consumed token; this regression re-loses that recovery — suggestion: keep the account gate but allow adoption when `store_refresh differs and not store_access` (entry keeps its still-valid access, gains the unconsumed refresh).

2. Same function, earlier line: when the *entry* has an empty `access_token` (a freshly created pool entry pre-first-mint), `entry_account` is `None` and the same-account gate **refuses adoption unconditionally** — if initial population from auth.json flows through here, first mint breaks — suggestion: allow adoption when `entry_account is None` (nothing to contradict) while still refusing an actual *mismatch*, and add tests for both empty-entry-access and missing-store-claims shapes.

3. Nit (`agent/agent_runtime_helpers.py` `codex_account_identity`): silently returning `None` on malformed JWTs makes the whole identity chain fail closed (good), but a single `logger.debug` there would distinguish "not a codex JWT" from "corrupt token" during support triage.

The rest is excellent: the stable `chatgpt_account_id` claim as identity anchor, `entry_id_for_account_identity` requiring unambiguous matches, singleton adoption gated on same-account (avoiding both silent account swap *and* needless consumption of single-use refresh grants), `_swap_credential` refreshing the identity on swap, and a genuinely strong test matrix down to signature-free JWT fixtures.

— reviewer-a · automated agent review (Hermes week-review)
