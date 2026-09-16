> AI code review — automated review for reference; please use your judgment.

1. apps/desktop/src/components/assistant-ui/thread/user-message.tsx:533 — CopyButton presumably writes through navigator.clipboard; in Electron contexts where that API is unavailable (file:// restrictions, older webviews) the desktop exposes the hermesDesktop.writeClipboard bridge — the e2e test uses the bridge only as a *verification* oracle. Why it matters: on a machine where the renderer lacks the async clipboard API, the new button would silently no-op at the feature's primary surface. Suggestion: confirm CopyButton falls back to the bridge (or add it), and extend the unit test with a missing-navigator.clipboard case.

2. Restructure check (no action needed): moving the container to `hasBody` forces the inner restore branch to be explicitly guarded (`showRestore ? … : null`) — the old ternary only worked because the container itself required showStop||showRestore. The new form is correct and also fixes padding honestly (pr-16 fits two icon buttons plus gap).

Exemplary test layering: the unit test pins raw-text fidelity (backticks, newline, Hangul) and that copy never opens the edit composer, while the Playwright spec proves it end-to-end through the real clipboard using a sentinel round-trip — including verifying the sentinel BEFORE clicking so a stale clipboard can't false-pass.
