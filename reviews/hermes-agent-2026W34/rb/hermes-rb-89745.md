> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix for a silently-dead setting: the normalizer rebuilt custom-provider entries from an allowlist that omitted the output-cap keys, so `_lift_max_output_tokens` never saw them and every startup logged an "unknown config keys ignored" warning — adding them to the known set *and* copying them through (with `max_output_tokens` taking precedence over the `max_tokens` alias, positive-int guarded) restores the documented behavior end to end.

Nit (non-blocking): no test accompanies the fix — this is a two-assert case (`_normalize_custom_provider_entry` preserves `max_output_tokens: 8192`, and a `max_tokens: 4096` alias maps to `max_output_tokens`), and given the setting already regressed once by being dropped, pinning it would prevent exactly that recurrence.
