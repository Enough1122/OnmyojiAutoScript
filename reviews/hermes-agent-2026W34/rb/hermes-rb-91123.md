> AI code review — automated review for reference; please use your judgment.

Nice resolution of a genuinely nasty parsing ambiguity, and the fail-closed choice (reject rather than guess) is backed by tests that also assert the config file is byte-identical after rejection — exactly the right regression harness.

- hermes_cli/config.py:1020 — issue — `_CUSTOM_PROVIDER_MODEL_OVERRIDE_FIELDS` is a hand-maintained allowlist duplicated away from wherever model-override fields are actually defined/consumed — why it matters — when a third model-level field ships, whoever adds it won't know this list exists, and every user attempt to set it dies with "ambiguous ... can only address context_length, prompt_caching", which reads as a bug report against config.py — suggestion — define the set next to the model-override schema (or derive both from one constant) and leave a pointer comment here; also document the inherent limitation that a model *named* like `vendor.context_length` cannot be addressed (the parser must read that as an override field).

- tests/hermes_cli/test_set_config_value.py:305 — issue (coverage) — only `context_length` exercises the happy path; `prompt_caching` has no create/update test despite being half the allowlist — why it matters — the two fields flow through different value-coercion downstream (`prompt_caching` is boolean-ish), so a coercion bug would ship untested — suggestion — parametrize the two positive tests over both fields.

- hermes_cli/config.py:1040 — nit — the ValueError message lists allowed fields but not the expected shape; appending one concrete example (e.g., `custom_providers.0.models.<model-id>.context_length`) makes the CLI self-teaching on failure.

No blocking issues found.

— reviewer-b (automated review)
