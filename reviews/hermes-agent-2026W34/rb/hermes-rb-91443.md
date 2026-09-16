> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right-sized fix: `max-w-3xl` caps the wordmark so `fit-text` stops inflating the type across ultrawide viewports, while `mx-auto` keeps it visually centered and the existing `--fit-min` floor still protects small windows. No behavioral risk elsewhere since the element is purely presentational and keeps its `aria-label`.

Nit (non-blocking): apps/desktop/src/components/chat/intro.tsx:171 — the cap is a bare utility class inline; if other hero/marketing surfaces later need the same ceiling, consider hoisting it into a shared token/class so the wordmark's maximum width doesn't drift between surfaces. Purely a maintainability note.

No blocking issues found.
