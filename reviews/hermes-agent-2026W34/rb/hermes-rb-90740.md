> AI code review — automated review for reference; please use your judgment.

Review of "feat(dashboard): add subscription API-equivalent cost". Careful observability feature: strictly opt-in (`show_api_equivalent_cost` default False), canonical billing untouched, provider mapping restricted to a vetted table (codex→openai), the legacy-residual computation explicitly mirrors `InsightsEngine._compute_model_breakdown`, and unpriced-token accounting keeps the shadow honest. Suggestions:

1. agent/usage_pricing.py:1536 (asymmetric labeling) — the PRICED path appends "API-equivalent estimate only; not a provider invoice." but the amount_usd-is-None early return hands back the raw result WITHOUT that note — downstream renderers keying on the label could display an unlabeled number; attach the disclaimer in both branches (or expose a dedicated `is_api_equivalent` flag on CostResult).

2. hermes_cli/web_server.py:15410 (pricing source fan-out) — `_price()` runs one `estimate_usage_cost` per route row on every analytics request; if rate resolution can hit the network (`source`/`fetched_at` fields hint at fetched tables), a 30-day dashboard with many model switches could trigger dozens of lookups per refresh — worth confirming the pricing table is cached/local, and hoisting the resolver out of the loop if not.

3. agent/usage_pricing.py:1507 (mapping governance) — `_API_EQUIVALENT_PROVIDERS` currently hardcodes one entry; document where the next subscription provider gets registered (and who verifies its public-rate equivalence), otherwise this stays codex-only forever by inertia.

4. hermes_cli/web_server.py:15558 (nit, contract clarity) — when the flag is off, `total_api_equivalent_cost`/`api_equivalent_unpriced_tokens` are emitted as explicit nulls rather than omitted; explicit nulls are the better choice, but say so in the dashboard payload docs so clients don't treat absence and null differently.
