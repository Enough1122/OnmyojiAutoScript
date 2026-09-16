> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Complete fix for the #89874 collapse, with the two subtle parts handled explicitly and tested: the seeded entry fingerprints the CALLER'S configured headers rather than any probe-synthesized Authorization (so the later cache_only lookup can actually match), and the grouped-provider lookups read the transport-resolved `api_mode` instead of the absent `ep_cfg["api_mode"]` key. The empty-list-is-authoritative shadowing semantics are documented in the docstring, and the round-trip test proves seed -> cache_only retrieval end to end through a real temp file.

Nit: every --refresh picker open now rewrites provider_models_cache.json even when the catalog and fingerprint are unchanged; a cheap equality check before _save_provider_models_cache would skip the write (and its mtime churn) in the common case.

No blocking issues found.