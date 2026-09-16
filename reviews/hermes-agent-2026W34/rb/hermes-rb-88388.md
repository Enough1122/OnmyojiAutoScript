> AI code review — automated review for reference; please use your judgment.

Right fix at the right seam: the insufficient-messages floor existed to protect LLM-summarization viability, but it also gated the *free* Phase-1 tool-result prune that needs neither a minimum message count nor an API call — so a 7-message transcript sitting 46K tokens over threshold wedged into model degeneracy while a cheap shrink was available. Running the prune (including the #61932 pressure pass) before conceding the no-op, then returning early only when it made progress, is exactly right. Points:

1. agent/context_compressor.py:~6955 — when the prune shrinks something but the result is *still* over threshold, the turn proceeds undersized rather than escalating to full compaction; the next `should_compress` cycle re-runs, finds nothing left to prune, and lands in the original no-op branch which correctly starts counting ineffectiveness. That ladder terminates properly — worth one comment noting the second-pass behavior so nobody "fixes" the counter bump away. (nit)
2. The test deliberately uses distinct tool bodies to isolate the pressure pass from dedup effects, and asserts the anti-thrash counter stays untouched on the progress path — both are the right invariants. (positive)
3. nit: the ratio assertion (`< total_before * 0.6`) is robustly loose as commented; consider also asserting the protected head/tail rows survive verbatim, since that's the other half of the contract. (nit)

No blocking issues found.
