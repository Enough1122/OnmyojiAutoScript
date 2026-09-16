> AI code review — automated review for reference; please use your judgment.

Review of "fix(agent): scope custom request overrides to runtime route" (sampled: agent_init ownership machinery, runtime restore hooks, tests). This fixes a real class of stale-extra-body bugs: previously Hermes-injected extra_body values were indistinguishable from caller/runtime-owned ones, so fallback→restore cycles either clobbered deliberate caller overrides or resurrected stale injected fields. The owned-leaves tracking (`_merge_provider_defaults_with_caller` returning what remains provider-owned, `_remove_provider_owned_values` preserving anything the caller changed post-injection) is the right model, identity resolution is fail-closed when the native catalog is unavailable, and fallback/restore snapshots now carry both the overrides and their ownership map — with a compatibility branch for old bare snapshots. Suggestions:

1. agent/agent_init.py:_merge_custom_provider_extra_body (cycle testing) — the ownership bookkeeping spans switch_model, try_activate_fallback, and restore_primary_runtime; add one integration-style test running several fallback→restore→switch_model cycles back-to-back and asserting the effective extra_body and owned set converge (no owned-leaf accumulation or loss), since each transition copies deep structures that must stay consistent.

2. nit — the hardcoded `{"openai", "github", "github-copilot"}` addition to native_provider_ids deserves a comment naming why those three are treated as native even without a catalog (route aliases?).

3. scope note — 45KB across 7 files but single-concern (override scoping); tests cover the identity matrix well.
