> AI code review — automated review for reference; please use your judgment.

Review of "feat(agent): allow pre_llm_call hooks to route the answerer model". Sound design: provider-change routes go through the same resolver as `/model` (so a hook can't pair a provider label with a foreign base_url — it can only reach providers configured locally), same-provider swaps skip the resolver round-trip, first matching hook wins deterministically, and resolve/switch failures fail open with a warning so a broken router never kills the turn. Suggestions:

1. agent/turn_context.py:1281 (no tests) — this adds a PLUGIN-FACING CONTRACT (hooks may return `{"model", "provider"}`) with zero test coverage in a single-file PR — please add unit tests for: first-match-wins among multiple routing hooks, the provider-change path (mock `switch_model`/`model_switch`, assert resolved creds are forwarded), the same-provider direct path, and the resolve-failure fallback that keeps the current model — this is exactly the surface a future refactor will silently break.

2. agent/turn_context.py:1301 (call-shape asymmetry) — the provider-change branch calls `agent.switch_model(..., api_key=…, base_url=…, api_mode=…)` by keyword while the same-provider branch passes the credentials POSITIONALLY — if switch_model's signature ever grows or reorders parameters (or those become keyword-only), one path breaks and not the other; use the keyword form in both branches.

3. agent/turn_context.py:1285 (discoverability) — the hook-result contract lives only in a code comment inside build_turn_context; the authoritative hook documentation (pre_llm_call's entry in hermes_cli/plugins.py and the plugin docs) should gain the `{"model", "provider"}` return shape, otherwise plugin authors can't discover the feature.

4. agent/turn_context.py:1293 (nit) — `_routed_model != getattr(agent, "model", "")` is case-sensitive; a hook returning the current model with different casing triggers a pointless client rebuild — compare case-insensitively like the provider check below it.

No blocking issues found, but item 1 deserves tests before this ships as a public hook surface.
