> AI code review — automated review for reference; please use your judgment.

1. agent/usage_pricing.py:1410 — the exclusion list (`mode != "anthropic_messages"`, `!= "codex_responses"`, `provider != "anthropic"`) must cover *every* mode whose usage shape legitimately lacks these four cache fields. Why it matters: any other supported mode (e.g. Gemini-style native wires or provider-specific branches further down in this function) would produce a permanent debug line claiming "provider is not sending cached_tokens" even when the shape simply differs — noisy triage signal that trains people to ignore it. Suggestion: derive the gate from the same branch predicate that routes parsing above (one source of truth), or enumerate-and-test each additional mode like the codex case was.

2. agent/usage_pricing.py:1447 — nit: the log text hardcodes `cache_read_tokens=0`, but execution continues into later branches (e.g. the MiniMax floor handling directly below) that can still populate cache_read from other signals; the accurate claim is about the *payload*, not the final value. Reword to "payload carries no cache-hit field" to avoid misleading greps.

3. agent/usage_pricing.py:1410 — style nit: `mode != A and mode != B and provider != C` reads cleaner as `mode not in {"anthropic_messages", "codex_responses"} and provider_name != "anthropic"`, matching how the sibling conditions are grouped.

Well-executed observability change: level-gated before any introspection work, presence-based checks that correctly catch the stripped-inner-key proxy pattern, defensive key listing with an `<unintrospectable>` fallback, and eight focused tests covering dict/SDK objects, both exclusion paths, the nested-strip case, and quiet-on-present behavior.
