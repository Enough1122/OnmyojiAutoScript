> AI code review — automated review; please use your judgment.

1. `agent/transports/chat_completions.py:~603–610` — the arm checks only that `effort` normalizes into the wire set; it never consults `enabled`. A config of ````{"enabled": False, "effort": "high"}```` — plausible for someone who turned thinking off but left the level configured — emits `reasoning_effort: "high"`, silently *re-enabling* reasoning server-side, the exact class of surprise the "unset omits" test exists to prevent — why it matters: the existing disabled-case test uses `{"enabled": False}` with no effort key, so this combination ships untested and wrong — suggestion: require ````reasoning_config.get("enabled")```` before reading `effort`, and add the disabled-with-effort case to the matrix.

2. Nit: the `{"low", "medium", "high"}` wire set is now spelled inline here while sibling arms define their own accepted sets nearby; hoisting one module-level constant (with a comment that it's the OpenAI wire vocabulary, not each provider's capability) keeps future level additions consistent across arms.

Otherwise clean: identity pass-through without inventing values, deliberate omission over defaults, no `supports_reasoning` side effects, the Kimi mutual-exclusion negative, and the messages-byte-identical assertion are all the right tests for this kind of request-shaping change.

— reviewer-a · automated agent review (Hermes week-review)
