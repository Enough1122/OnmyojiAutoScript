> AI code review — automated review for reference; please use your judgment.

Right-sized fix: clearing `$newChatProfile` when the Cursor-style fresh tile opens means a stale picker selection can't silently scope an unrelated new session, and resetting to `null` (primary) matches the documented semantics of that atom.

- apps/desktop/src/app/contrib/wiring.tsx:836 — issue (verification/coverage) — this resets only *one* of the new-session entry points; please confirm the other paths that open a fresh session (keybinding-driven new tab, command-palette action, any deep link) either share `openNewSessionTab` or apply the same reset — why it matters — partial coverage reproduces #91089 through whichever door was missed, and nothing here pins the behavior with a test asserting `$newChatProfile.get() === null` after tile open.

No blocking issues found.

— reviewer-b (automated review)
