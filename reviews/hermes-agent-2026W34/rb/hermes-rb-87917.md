> AI code review — automated review for reference; please use your judgment.

Review of "fix(auxiliary): omit disabled reasoning field for Gemini endpoints". Correctly scoped fix: Gemini's OpenAI-compatible endpoint rejects the `reasoning` key outright, so a DISABLED config must be omitted (omission is semantically equivalent — Gemini never reasons unless asked) while enabled configs and non-Gemini providers keep their fields, all pinned by a well-shaped parametrized test suite including the via-reasoning_config path. One gap:

1. agent/auxiliary_client.py:8570 (exact-shape match) — the omit fires only on the exact dict `{"enabled": False}`; a merged config like `{"enabled": False, "effort": "low"}` (effort left over from an earlier setting alongside a later disable) serializes anyway and 400s on Gemini again — consider popping whenever `merged_extra["reasoning"].get("enabled") is False` regardless of sibling keys, keeping any OTHER keys intact.
