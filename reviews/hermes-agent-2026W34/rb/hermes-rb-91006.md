> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Well-evidenced fix: the live dose-response verification (effort low/medium/high mapping to ~1K/3K/8.4K thinking chars while \`budget_tokens\` is silently ignored) is exactly the right way to justify reclassifying a family onto the adaptive contract, and the docstring records it for posterity. The \`^glm-5(?:[.\-p]|$)\` matcher correctly includes \`glm-5\`, \`glm-5.3\`, \`glm-5-turbo\`, relay spellings like \`glm-5p2\`, excludes \`glm-4.*\`/\`glm50\`, handles vendor prefixes and None/casing, and the tests pin all of that plus the built wire kwargs (adaptive contract emitted, no budget_tokens leakage, low-effort ask stays low).

Nit: both \`_model_name_is_kimi_family\` and the new GLM checker now independently implement "normalize → strip vendor prefix → match family pattern"; extracting a tiny shared \`_strip_vendor_prefix(model)\` (or a family-regex table) would keep the two from drifting when the next provider-specific spelling shows up.

No blocking issues found.