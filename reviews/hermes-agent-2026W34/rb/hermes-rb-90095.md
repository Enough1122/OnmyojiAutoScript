> AI code review — automated review; please use your judgment.

1. `hermes_cli/web_server.py` (`list_custom_endpoints` → `_apply_live_custom_endpoint_catalogs`) — every **GET** of the endpoints list now performs a live `GET {base_url}/models` per endpoint with `discover_models` on, serially, with an 8s timeout each — why it matters: opening the dashboard Settings panel becomes O(endpoints × up-to-8s) against third-party hosts the user may not want probed that often, and N endpoints stack into tens of seconds before the panel renders — suggestion: add a short TTL cache (per endpoint id), honor an explicit `?discover=1` query param so plain lists stay cheap, or at least run the probes concurrently with a bounded overall deadline.

2. Nit (`_apply_live_custom_endpoint_catalogs`): the probe uses stored credentials (`key_env` resolution included) on every list read — combined with item 1 that's recurring authenticated traffic to custom gateways without a user action; worth stating in the docs row for `discover_models` so the behavior is consented-to rather than surprising.

3. Nit (`:~8220–8232`): the Save-path probe runs synchronously inside the POST handler; a slow endpoint now delays Save by up to 8s even though the typed model would persist regardless — consider fire-and-forget discovery with the next GET filling it in, since the GET path already merges discovered models.

Everything else is solid: Anthropic-compat detection (explicit mode, normalized spellings, and base-URL inference) with exact header assertions including the *absence* of `Authorization`, merge semantics keeping typed/stored order first, graceful degradation to the typed model when the catalog is unreachable on both Save and GET, `discover_models=false` fully suppressing probes, and the shared test client thoughtfully stubbing the new prober so legacy tests don't hit DNS.

— reviewer-a · automated agent review (Hermes week-review)
