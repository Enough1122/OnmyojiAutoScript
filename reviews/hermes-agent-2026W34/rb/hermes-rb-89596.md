> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): route link/artifact-click preview opens through loopback reach". Right fix for an easy-to-miss remote-mode bug: localhost URLs detected in tool output or surfaced by the agent name the GATEWAY's loopback, so both the artifact row and clicked links now get the same reach resolution the address bar already had — while `source`/`label` keep the address the link actually said (tested explicitly, which is the detail most implementations forget). Suggestions:

1. apps/desktop/src/lib/external-link.tsx:242 (unhandled rejection) — the `void Promise.all([...]).then(async ...)` chain has no catch, and `reachablePreviewUrl` can reject (bridge unavailable, reach probe failure); that turns into an unhandled promise rejection in the main window instead of a preview — append `.catch(() => openPreview({ kind: 'url', label: hostPathLabel(target), source: target, url: target }, 'explicit-link'))` so reach failure degrades to today's direct-open behavior. (PreviewStatusRow already try/catches, so only this path is exposed.)

2. nit — worth one sentence on `reachablePreviewUrl`'s contract in the review/docs (no-op passthrough for public URLs? bridge-only on remote mode?) since two new call sites now depend on its cheap-path behavior for EVERY clicked web link.
