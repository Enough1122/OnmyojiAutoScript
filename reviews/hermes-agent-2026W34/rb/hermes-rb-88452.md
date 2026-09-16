> AI code review — automated review for reference; please use your judgment.

Both root causes are real: a 64-token cap dies inside `<think>` on reasoning models before any JSON appears (documented with an actual M2.7 measurement), and json_schema rejection is exactly what several providers do. The retry-without-response_format fallback plus `_extract_title_text`'s existing think-strip/fence handling is the right recovery shape, and the tests pin call counts *and* per-call kwargs. Points:

1. agent/title_generator.py:~423 — the except is **all exceptions**, so a genuine timeout or auth failure now triggers a second full LLM call: doubled latency on every real failure, two hits against a rate-limited provider per session, and the failure_callback reports e2 rather than the more informative e. Narrow the retry to the structured-output rejection signature (status 400/422, or "response_format" in str(e)) and let everything else fail through to the original handler.
2. max_tokens 64 → 512 applies unconditionally — an 8× token-cost increase on providers that accept json_schema and need ~30 tokens. Consider keeping the small default and escalating only when the first response shows reasoning leakage/truncation, or gating on a reasoning-capable model list. Real cost at session-per-message title rates. (moderate)
3. The retry duplicates the entire call block; a tiny `def _attempt(use_response_format)` closure would keep the two paths from drifting (they already differ only in extra_body). (nit)
4. The comment citing verified M2.7 behavior and the surveyed-implementations docstring are good evidence-based context. (positive)

No blocking issues found beyond items 1–2's cost profile.
