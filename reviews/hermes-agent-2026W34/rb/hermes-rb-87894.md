> AI code review — automated review for reference; please use your judgment.

1. plugins/memory/holographic/store.py:`_add` — Positive: replacing the ASCII `_RE_CAPITALIZED` with a `\w`-Unicode word tokenizer plus `isupper` checks handles Cyrillic (and any script) without needing `p{Lu}` escapes Python's `re` lacks, and the capitalized-run accumulation with whitespace-separation tracking preserves multi-word name extraction ("Иван Петров" linked as one entity — tested against the real store).

2. retrieval.py:`probe` — Positive: resolving entities in Python via `casefold()` fixes SQLite's ASCII-only NOCASE for Unicode scripts, preferring exact relational links over noisy HRR ranking for known names while keeping the algebraic path as fallback for unknowns — both sides covered by tests (casefolded query returns only the linked fact).

3. Nit: the new prompt patterns cover a handful of Russian preference/decision verbs; consider noting in SKILL/docs that extraction remains pattern-based per language rather than implying full multilingual coverage. No change requested beyond that.