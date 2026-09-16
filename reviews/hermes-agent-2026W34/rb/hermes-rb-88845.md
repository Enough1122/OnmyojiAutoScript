> AI code review — automated review for reference; please use your judgment.

Right fix: aggregator semantics (vendor/model slug acceptance) were hardcoded to registry providers only, so a user-configured OpenRouter-style entry got false "unrecognised provider" warnings in doctor. The opt-in `is_aggregator` flag with fail-safe resolution and the `auto`/`custom` exclusion is the right shape. One nit:

- hermes_cli/providers.py:750 — nit (docs) — `is_aggregator` is a new accepted key on user `providers:` entries but isn't in the config schema/example docs; users can't discover the flag that silences their false positives — add it to the providers config reference with one line.

No blocking issues found.

— reviewer-b (automated review)
