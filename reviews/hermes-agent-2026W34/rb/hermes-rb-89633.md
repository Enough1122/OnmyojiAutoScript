> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): exec get-windows helper from app.asar.unpacked". Excellent packaged-Electron fix with unusually good diagnostics discipline: the asar redirect uses exact segment matching (with tests for dev-tree passthrough and the `app.asar-tools` lookalike), every previously swallowed failure path now records its CAUSE (`import.meta.resolve` throw, import throw, openWindows throw, non-array return) and surfaces it in the tool error plus console, and the comment explains why Electron's usual child_process asar rewriting doesn't apply in this ESM main process. Suggestions:

1. apps/desktop/electron/window-below.ts (stale failure note) — `lastEnumerationFailure` is set on every failure but never cleared on SUCCESS, so one old cause (e.g. a transient ENOTDIR) stays attached forever; if a future code path returns null without calling `noteEnumerationFailure` first, `readWindowBelow` will attribute that new failure to the stale reason — clear the field whenever `enumerateViaGetWindows` returns a real window list.

2. nit — `describe(error)` reads `.code` off any thrown value; for non-Error throws without a code property this yields undefined gracefully, fine — just noting the helper silently normalizes strings and errors alike, which the tests don't yet pin.
