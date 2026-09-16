> AI code review — automated review for reference; please use your judgment.

Right fix, right layer: WeChat's renderer treats server-inserted newlines as paragraph breaks and drops their indent, so keeping each list item on one physical line and letting the client wrap natively is correct — and exempting at the wrap site (rather than post-processing) keeps tables/fences untouched. The regex thoughtfully covers bullets, ordered `10.`/`1)`, full-width `（1）`, and GitHub-style checkboxes. Small notes:

1. gateway/platforms/weixin.py:~183 — two CJK-adjacent marker styles are still unwrapped-candidates: `1、` (Chinese enumeration comma) and bare `一、`-style ordinals. For a WeChat-specific formatter these are common in LLM output aimed at CN users; adding `d+[、]` (and optionally `[一二三四五六七八九十]+、`) to the alternation would close the most likely follow-up bug report. (nit)
2. The checkbox group requires whitespace after `[x]` (`[x] text`); `[x]**bold**`-style dense output slips through and gets wrapped mid-item. Trivial edge. (nit)
3. tests — parametrize covers `-` and `10.`; adding one bullet (`•`) and one full-width case would lock the whole character class against future regex edits. (nit)

No blocking issues found.
