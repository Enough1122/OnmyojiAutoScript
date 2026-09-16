> AI code review — automated review for reference; please use your judgment.

Consistent triple-update (dependency, `build.electronVersion`, allowed-builds pin). Two small things:

- package.json — issue (verification) — this is a *major* Electron jump (40 → 41); please confirm native modules that bind to Electron's ABI (notably `node-pty`) were rebuilt/validated against the new headers on all three platforms — why it matters — an ABI mismatch typically surfaces as a renderer/main crash at first terminal open, not at install time, so CI green on lint/typecheck proves nothing here — suggestion — note in the PR description which platforms had a full packaged smoke test of the embedded terminal.

- apps/desktop/package.json:298 — nit — the edit dropped the trailing newline at EOF (`\ No newline at end of file`); trivially fixable and keeps diffs clean for the next bump.

No blocking issues found.

— reviewer-b (automated review)
