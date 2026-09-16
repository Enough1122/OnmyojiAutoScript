> AI code review — automated review for reference; please use your judgment.

Reviewed the diff — small, clean addition: reuses the existing PaneStripGlyph pattern, wires i18n via t.common.close, and delegates to the shared closeRightRailTab(BROWSER_TAB_ID) action rather than inventing local state handling.

Nit: apps/desktop/src/app/chat/right-rail/preview-browser-bar.tsx:201-205 — the handler assumes BROWSER_TAB_ID is always the active/open tab; if the bar can ever render while the rail was closed through another path, a cheap guard (or asserting the store contract in a comment) would make the invariant explicit.

No blocking issues found.