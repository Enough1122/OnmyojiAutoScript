> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Well-assembled fix for a real gap: named local endpoints (\`ollama-launch\`) silently missed everything CustomProfile provides — max_tokens floor, \`reasoning_effort\`, \`num_ctx\`, and now the qwen3.8 user-query injection that keeps Ollama's renderer from 500ing on tool loops (#17778). The resolver ladder is conservative (registered profile wins; local-server detection failure degrades to the legacy path), \`prepare_messages\` is documented wire-only and proven non-mutating, insertion skips leading system blocks, and the test set covers the full matrix including the \`<tool_response>\`-wrapper negative and effort clamping never escalating.

Points worth a deliberate look:

- **Scope is wider than the title.** The fallback attaches CustomProfile to *any* unnamed provider on a local endpoint where \`detect_local_server_type\` says \`vllm\` or \`llamacpp\`, not just Ollama. That's likely intended (they share the OpenAI-compat shape), but it means vLLM/llama.cpp users start receiving \`options.num_ctx\` extra-body keys and think-handling they never got before. Most stacks ignore unknown keys, but confirming inertness (or gating the Ollama-specific extras on server_type == "ollama") would make the widening explicit rather than incidental.

- **Global user-query scan vs renderer expectations.** \`_has_plain_user_query\` searches the entire history, so one early user message suppresses injection forever even if the current tail is a long pure tool-loop. If Ollama's validateMessages only needs *any* plain user turn (as the issue suggests), this matches — worth a comment citing that semantic so a future Ollama change to "recent window" gets noticed.

Nit: \`custom_endpoint_efforts\` matches \\"qwen3.8\" via bare substring, so a hypothetical future \\"qwen3.80\\-something\\" would inherit the narrow vocabulary; the regex-boundary style used by the GLM family matcher would be more future-proof.

No blocking issues found.