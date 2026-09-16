> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Trivial, correctly placed catalog addition (variant slotted beside \`glm-5.2\` in the zai curated list).

Nit: confirm \`agent/model_metadata.py\` resolves context length for the suffixed slug — \`glm-5.2\` maps to 1M via its explicit entry, and whether \`glm-5.2-highspeed\` inherits that depends on the lookup being prefix-based vs exact; if exact, the variant would silently fall back to the generic 202K \`glm\` floor and compress ~5× too early (the very regression #91039 just fixed for \`glm-5.3\`). A one-line entry or a pinned test would settle it.

No blocking issues found.