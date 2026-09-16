> AI code review — automated review for reference; please use your judgment.

Right-sized defensive fix: widening `baseKeyFromCode` to `unknown` and failing closed on non-string/empty codes is correct, and the guard sits at the right layer (below the key-path fallback).

- apps/desktop/src/lib/keybinds/combo.test.ts:221 — issue (coverage) — only the "both absent" shape is pinned; the neighboring malformed shapes are not: `code = null`, `code = 42` (number), and especially `code = ""` *with* a valid `key` (must still resolve via the key path rather than being dropped) — why it matters — the fix should make junk codes inert without degrading legitimate events whose `code` is merely empty (some IME/synthetic events do exactly that), and the current test can't distinguish those outcomes — suggestion — add the three parametrized cases, asserting null-combo vs key-path resolution respectively.

No blocking issues found.

— reviewer-b (automated review)
