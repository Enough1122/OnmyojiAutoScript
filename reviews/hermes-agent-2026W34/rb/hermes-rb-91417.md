> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right fix shape: one `cellText()` helper (strip markup → TeX→Unicode) now feeds *both* the width math (`stringWidth`, min-word width, padding) and what's actually drawn, across every table path — wrapped, single-line, and vertical/compact fallbacks. Measuring exactly what you render is precisely what makes column splits stop drifting on math-bearing cells, and renaming the shadowing `cellText` local to `lineContent` keeps the helper reachable there. Two cosmetic slips worth sweeping before merge: a stray all-whitespace line before `line += lineContent + pad`, and the NOTE comments contain a literal tab where `$\to$` was meant (`$	o$`).

Nit (non-blocking): no regression test pins the actual bug — `renderTable`'s width/wrap logic is pure enough to unit-test (e.g. a row with `$	o$` plus a full-width CJK char must measure equal to its drawn width, and pads must sum to the column width). Without it, the next markup transform added to only one of the two paths re-introduces silent misalignment.
