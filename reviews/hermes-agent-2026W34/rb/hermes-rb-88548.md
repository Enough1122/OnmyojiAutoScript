> AI code review — automated review for reference; please use your judgment.

Right kind of fix: pinning `get_model_capabilities` to a text-only caps object removes the hidden dependency on whatever the models.dev lookup returns in a given environment (network state, cache freshness), which is what made this "text-only routing" test non-hermetic; the stub is placed before the resolver call and scoped via monkeypatch, so no leakage into sibling tests.

No blocking issues found.

Nit: consider counting invocations on the stub (`calls.append(...)`) and asserting it was consulted at least once — if a future refactor changes *where* the resolver gets its capabilities from, today's version would silently stop exercising the stubbed path and the hermeticity guarantee would erode without any test noticing.

— Reviewed by Hermes AI reviewer (reviewer-f2)
