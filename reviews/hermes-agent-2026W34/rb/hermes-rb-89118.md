> AI code review — automated review for reference; please use your judgment.

Complete plumbing job for #88997: all three spellings normalize to one canonical key (`max_output_tokens`), the unknown-key warning can't fire for any accepted spelling, the field reaches `_custom_provider_entry_to_provider_config`'s pass-through list *and* the schema-validating `_VALID_CUSTOM_PROVIDER_FIELDS` set (the place similar fixes historically forgot), and tests cover warning-free preservation, the alias chain, and actual runtime-resolution propagation rather than just the normalizer's return dict.

No blocking issues found.

Nit: `isinstance(max_output_tokens, int) and > 0` accepts `true` (bools are ints in Python), persisting `max_output_tokens: 1` from a YAML `max_output_tokens: true` typo — pre-existing shape shared with `context_length`/`rate_limit_delay`, so not this PR's bug, but a single `and not isinstance(x, bool)` guard (or one shared `_positive_int()` helper) applied while the field is fresh would close the whole class.

— Reviewed by Hermes AI reviewer (reviewer-f2)
