> AI code review — automated review for reference; please use your judgment.

Review of "feat: add SSYCloud(胜算云) LLM provider". Model provider addition done by the book: plugin profile with aliases (`shengsuanyun`, `ssy-cloud`) registered through the real discovery path, aggregator classification applied consistently across BOTH normalization layers and the catalog grouping, Hermes overlay with env-var wiring, version-pinned fallback models keeping native vendor prefixes, docs table row, and tests that exercise discovery/registry/normalization end-to-end under an isolated HERMES_HOME rather than mocking the registry. One nit:

- plugins/model-providers/ssycloud/__init__.py — unlike some recently added providers (e.g. DeepInfra's `DEEPINFRA_BASE_URL` override), there is no base-URL override env for users fronting the router with a proxy or on-prem gateway; consider adding `SSYCLOUD_BASE_URL` now while the surface is being defined.

No blocking issues found.
