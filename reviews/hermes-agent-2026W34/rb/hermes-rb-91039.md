> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Clean data addition: \`glm-5.3\` gets the same 1M context entry as 5.2 (with source and verification date noted), correctly placed above the generic \`glm\` 202K fallback so prefix matching can't down-grade it, and the Z.AI curated list gains the new model at the top of the newest-first ordering.

Nit: worth a one-line unit test pinning \`resolve context_length("glm-5.3") == 1_048_576\` — this exact table has regressed before per the comment's own history ("glm-5.2 resolves to 1M while older variants hit the generic fallback"), and a pinned assertion makes the next model bump copy-paste-safe.

No blocking issues found.