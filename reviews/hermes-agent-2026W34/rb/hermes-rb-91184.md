> AI code review — automated review for reference; please use your judgment.

1. `plugins/kanban/dashboard/dist/index.js:~2786–2792` (`handleMouseDown`) — the new `props.view === "wrapped"` guard reads `props.view` inside a `useCallback`, but the visible hunk doesn't touch that callback's **dependency array** (`checkScrollable` correctly got `[props.view]`; this one didn't) — why it matters: if its deps are still `[]`, the closure captures the initial view and mouse-panning stays armed in wrapped mode until a full remount, silently reintroducing sideways drag against an `overflow-x: hidden` container — suggestion: confirm/add `props.view` (or the whole `props`) to that callback's deps, and audit any wheel/autoscroll handlers in the same component for the same capture.

2. `plugins/kanban/dashboard/dist/index.js:~1308–1341` — wrapped mode turns off horizontal autoscroll surfaces, but column **drag-and-drop** was built around a horizontally scrollable strip; with columns wrapping onto multiple rows, auto-scroll-during-drag and drop-target hit-testing may behave differently (e.g., dragging toward the viewport edge no longer reveals off-row columns) — why it matters: wrapped is opt-in, so breakage here is contained, but users who switch will do exactly the heavy multi-column drags the mode invites — suggestion: sanity-check one cross-row drag in wrapped mode before merge, or note the limitation in the tooltip.

3. `plugins/kanban/dashboard/dist/index.js:~2497–2513` — the control's `title` tooltips are hardcoded English while the visible labels correctly go through `tx(t, ...)` — why it matters: localized UIs get translated buttons with English hover text — suggestion: route the three `title` strings through `tx()` too (`viewWideTitle`, `viewWrappedTitle`, `boardViewTitle`).

Nit (`:~305–320`): the localStorage read/write helpers duplicate the surrounding try/catch-quota pattern; a shared `safeStorageGet/Set` would shrink the file — cosmetic given the existing local style.

Overall: clean, self-contained feature with sensible defaults (wide preserved), global-not-per-board preference documented as intentional, and CSS that degrades gracefully (flex-basis floor keeps narrow windows usable). Item 1 is the only one that could bite functionally — please verify before merge.

— reviewer-a · automated agent review (Hermes week-review)
