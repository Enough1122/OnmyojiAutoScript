> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Strong PR overall: positive-only fail-closed detection, explicit-key-wins semantics, thorough regression tests including the metered direction. Points to consider:

- **agent/usage_pricing.py:~1100-1128 — pool fallback decides from the first usable credential, not the one actually used.** The loop \`return\`s on the highest-priority entry bearing a token, but pools routinely hold *both* an OAuth seat and a Console key; if runtime rotation/failover lands on the other entry mid-session, every cost report for those calls is priced under the wrong mode. Why it matters: this is the same two-directions-wrong problem the docstring describes. Suggestion: thread the *selected* credential into \`estimate_usage_cost\` (as already done for \`api_key\`) rather than re-deriving from the pool file here — or, minimally, detect a mixed-type pool and mark the result uncertain instead of silently committing to entry #1.

- **usage_pricing.py:~1112-1120 — priority ordering is duplicated and its direction is assumed.** \`sorted(entries, key=_priority)\` ascending encodes "lower = higher priority," and this ordering logic now lives independently of whatever \`hermes_cli.auth\` uses when selecting at request time. If either side changes, pricing silently disagrees with routing. Suggestion: expose/reuse a single selection helper (e.g. \`auth.select_pool_entries(provider)\`) so the two can't drift; add a comment pinning the convention next to \`read_credential_pool\`.

- **usage_pricing.py:~1085 — private cross-module import.** \`from agent.anthropic_adapter import _is_oauth_token\` couples pricing to a private symbol; a rename there degrades detection to \`False\` (fail-closed, so safe, but subscription users silently see phantom costs again — the very bug this PR fixes). Suggestion: promote it to a public \`is_oauth_token\` in the adapter, or define the predicate alongside the token constants it matches.

- **usage_pricing.py:197-216 — Opus 5 1h-TTL cache writes are known-undercounted but invisible to users.** The NOTE honestly documents the 60% undercount, yet nothing surfaces it at estimate time. Suggestion: when \`prompt_caching.cache_ttl == "1h"\` (or usage carries \`ephemeral_1h\` tokens), append a note to \`CostResult.notes\` ("cache-write estimate uses 5m-TTL rate") so consumers know why numbers differ from their Console invoice; longer term consider a second cache-write rate column.

- **usage_pricing.py:1076-1130 — hot-path cost.** \`_anthropic_is_subscription\` runs on every \`estimate_usage_cost\`; if \`read_credential_pool\` hits disk each time and estimates run per-turn/per-stream-event, this adds avoidable IO. Suggestion: memoize per provider for a few seconds (or per resolved credential fingerprint) unless the pool reader already caches.

- **tests/agent/test_usage_pricing_anthropic_subscription.py — small gaps.** Untested: the dict-shaped pool branch (\`{"anthropic": [...]}}\`, usage_pricing.py:~1098-1101), malformed/garbage pool payloads, and the mixed OAuth+API-key pool (pinning current first-entry behavior explicitly would document the point-1 limitation until it's fixed).

Nice touch adding the missing Opus 5 metered entry with source URL and version stamp.
