> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct one-line closure of a validation gap: roots like `platform_toolsets`, `known_plugin_toolsets`, `smart_model_routing`, `session_reset`, and `group_sessions_per_user` are genuinely read by the runtime but absent from `DEFAULT_CONFIG`, so `hermes config set` rejected valid keys with a bogus "did you mean platform_hints.cli" suggestion. Folding `_EXTRA_KNOWN_ROOT_KEYS` into the known-set union is exactly where the fix belongs, and the eight new parametrized cases pin each previously failing root (including dotted paths) so a future root-key regression can't sneak back.
