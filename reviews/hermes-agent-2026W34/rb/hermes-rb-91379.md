> AI code review — automated review for reference; please use your judgment.

1. tools/delegate_tool.py:4553 — the `or`-chain conflates "unset" with the documented `0 = uncapped` sentinel. Why it matters: a runtime explicitly configured with `max_output_tokens: 0` ("no cap") is skipped, and the global `delegation.max_output_tokens` cap silently applies instead — the most specific setting loses to the least specific one. The same conflation lets a *legacy* `max_tokens` beat an explicit modern `max_output_tokens: 0`. Suggestion: resolve with sentinels, e.g. `v = runtime.get("max_output_tokens"); if v is None: v = cfg.get("max_output_tokens"); if v is None: v = cfg.get("max_tokens")`, so explicit zeros win at each level.

2. tools/delegate_tool.py:4553 — the resolved value is passed through unvalidated. Why it matters: a typo'd string or float in YAML propagates straight into request parameters and fails opaquely at call time (or worse, gets coerced oddly by the provider client). Suggestion: coerce/validate once (`int(v)`, reject <= -1 with a clear config error) where the params builder consumes it.

3. tests — no coverage accompanies the change. Suggestion: a small precedence matrix — runtime-set / cfg-cap / legacy-only / all-unset, plus the explicit-`0`-beats-cfg case from item 1 (which fails under the current implementation and would pin the fix).

4. hermes_cli/config_defaults.py:1928 — the new knob is commented well in-code, but the user-facing docs tree this repo maintains (website/docs, where sibling delegation keys are described) isn't updated. Why it matters: users can't discover the cost bound without reading source. Suggestion: add a short entry next to `child_timeout_seconds` in the delegation docs page.
