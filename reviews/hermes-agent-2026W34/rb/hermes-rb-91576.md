> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Correct call for #91553: the DOM paste action executes webContents.paste() in main and resolves the system clipboard itself, so gating its enablement on the renderer-side readClipboard() probe coupled a UI fact to an unreliable signal (Win32 bridge reporting empty while the real paste path succeeds). The fix fails open with a harmless no-op, documents the asymmetry precisely where the next reader needs it (app-context-menu.tsx and the terminal-variant comment in store.ts), and narrows probeClipboard to the terminal kind via Extract so the type system now enforces the distinction. The kept gate on the terminal menu is right too, since that item inserts the read text itself.

Nit: tests currently pin the new fail-open behavior twice (app-context-menu.test.tsx) but nothing in this diff pins the *other* half of the contract — that the terminal menu still grays Paste on an empty clipboard. One store-level or component-level regression test there would protect the intentionally asymmetric behavior from being "simplified" back into uniformity later.

No blocking issues found.