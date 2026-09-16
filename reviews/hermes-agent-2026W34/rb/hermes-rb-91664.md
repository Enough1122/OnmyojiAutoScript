> AI code review — automated review for reference; please use your judgment.

Nice UX addition; the regression test pinning the fallback-link behavior (including the `data-hermes-context-menu-trigger` assertion) is a good touch, and keeping the lightbox outside the `asChild` merge is correctly reasoned. Items:

- apps/desktop/src/components/chat/reveal-in-folder.tsx:20 — issue — `isDesktopFsRemoteMode()` is evaluated once per render as a plain function call rather than derived from a reactive store subscription — why it matters — if the connection mode flips while this component stays mounted (switch gateway, reconnect), the gate decision is stale until some unrelated re-render, so reveal either silently disappears or (worse) fires against the wrong machine's disk — suggestion — read the connection/mode state via the same reactive source `FileEntryContextMenu` uses (e.g., `useStore($connection)`) so the gate updates live, or key the trigger on the connection identity.

- apps/desktop/src/components/chat/reveal-in-folder.tsx:31 — issue — `revealDesktopPath(path)` receives transcript-controlled strings unvalidated; on Windows a path like `\\\\server\\share\\file` makes Explorer attempt an SMB resolution just by opening the containing folder — why it matters — an agent-produced artifact name can cause unintended network access from the user's desktop with zero consent prompt — suggestion — reject UNC/device-path forms (`\\\\`, `\\\\?\\`) in the reveal handler with a gentle error toast, and note the policy next to the remote gate.

- apps/desktop/src/components/chat/reveal-in-folder.tsx:6 — issue (layering) — a shared chat component now imports `pickRevealLabel` from `@/app/right-sidebar/file-actions`, pulling an app-route module into the component graph — why it matters — invites circular imports (right-sidebar already renders chat-adjacent trees) and makes future code-splitting of the sidebar impossible — suggestion — hoist the label picker into `@/lib` or the i18n helpers and import from there on both sides.

- apps/desktop/src/components/chat/reveal-in-folder.tsx:47 — issue (a11y) — the menu is reachable only through a pointer `contextMenu` event; keyboard and screen-reader users get no way to reveal/copy since the wrapped anchors are plain links without a menu affordance — why it matters — the file trees this mirrors expose the same actions via focusable UI, so transcript artifacts become second-class — suggestion — either make the trigger focusable and open the menu on Enter/focus, or append a small always-visible overflow action alongside the hover download button.

- apps/desktop/src/components/assistant-ui/markdown-text.reveal-menu.test.tsx:30 — issue (coverage) — only the happy path of one surface is tested; the remote-mode children-passthrough branch, Copy Path (toast + clipboard write), and `ZoomableImage` with/without `revealPath` are unpinned — why it matters — the gate in item 1 and the lightbox-sibling restructuring are exactly the parts most likely to regress silently — suggestion — add three small cases: remote mode renders bare children, copy-path writes clipboard, image with no `revealPath` renders unwrapped.

No blocking issues found — items 1 and 2 deserve a look before merge.

— reviewer-b (automated review)
