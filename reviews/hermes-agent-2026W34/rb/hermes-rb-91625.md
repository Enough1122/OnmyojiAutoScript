> AI code review — automated review for reference; please use your judgment.

The CSS fix itself is textbook-correct: `min-w-0` on every grid/flex node in the width chain plus `shrink-0` on the icon-only button is exactly how this class of clipped-controls bug is solved, and the explanatory comment documenting *why* each link matters is genuinely useful for the next person.

- apps/desktop/src/plugins/hermes-bots/tests/routine-row-min-width.test.mjs:20 — issue — all five tests are regex assertions against source-string class literals, so they pin formatting rather than behavior: reordering Tailwind classes, switching `cn()` composition, or extracting the row into a shared component breaks them while a real regression elsewhere in the width chain passes — why it matters — these will decay into either noise (false reds on refactors) or false confidence, and the whitespace-sensitive negative assertion (`doesNotMatch` with an embedded multi-line pattern) is the most fragile of all — suggestion — acceptable as a stopgap for a single-file plugin artifact, but prefer a DOM-level render test (even happy-dom + the existing jsx runtime) asserting computed overflow/truncation classes on the rendered nodes, and drop the negative-formatting check entirely.

No blocking issues found — the production change is right; this is only about how it's guarded.

— reviewer-b (automated review)
