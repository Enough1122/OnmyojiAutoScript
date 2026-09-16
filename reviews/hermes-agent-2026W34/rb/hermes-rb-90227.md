> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): open chat links in the system browser by default". Right call, well-argued: the shipped hint already said "⌘/Ctrl-click for preview pane", so this aligns the router with its own copy AND with universal app conventions (bare click = logged-in system browser). The `openLink` default flip is explicit (`native !== false`), middle-click keeps the OS new-tab path, terminal links keep their documented inverse chords, and tests were updated on both sides of the inversion rather than just flipped assertions. Suggestions:

1. apps/desktop/src/lib/external-link.tsx:231 (call-site audit) — the DEFAULT flipped, so every `openLink(url)` caller that passed NO options silently changes destination; the diff updates directive-actions and ExternalLink, but please sweep the repo for remaining `openLink(` sites (preview tabs, markdown renderers, notification deep links) and decide each one deliberately — silent default flips are how "open docs" buttons end up yanking users out of the app.

2. apps/desktop/src/lib/external-link.tsx:207 (naming debt) — `wantsNativeBrowser` now returns true when the user asked for the IN-APP pane, and the call site inverts it (`native: !wantsNativeBrowser(...)`) — the name lies relative to both its modifiers and its effect; rename to `wantsPreviewPane`/`wantsInApp` before someone re-inverts an innocent-looking double negative.

3. apps/desktop/src/app/right-sidebar/terminal/links.ts:28 (documented asymmetry) — chat is bare=OS/⌘=pane while terminal stays ⌘=open/⇧⌘=OS; the code comment explains why terminal can't spend its chord elsewhere, but a line in the user-facing shortcut docs would stop this reading as an inconsistency bug later.

No blocking issues found.
