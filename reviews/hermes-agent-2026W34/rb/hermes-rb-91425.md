> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Sound approach: resolving the default browser via the UserChoice ProgId (https→http fallback), restricting to the two Chromium families whose `--app` + `--user-data-dir` combo the shim depends on, and keeping the full degradation ladder (shim → WinForms card → log-only) intact. The dedicated per-PID profile dir still guarantees a window this process owns, and the stale-profile sweep is good hygiene. Findings:

1. scripts/desktop-update/windows.ps1:139 — ProgId matching is exact-equality on `ChromeHTML`/`MSEdgeHTM`. Real machines do carry variant registrations (channel-specific Edge ProgIds like `MSEdgeHTMBeta`/`MSEdgeHTMDev`, and some enterprise images register suffixed Chrome ProgIds), where the user's *default* resolves to such a ProgId and the shim silently downgrades to the WinForms card despite a perfectly usable Chromium being default. A prefix match (`$progId -like "ChromeHTML*"` / `"MSEdgeHTM*"`) keeps the guard against non-Chromium browsers while tolerating channel/tenant suffixes.

2. scripts/desktop-update/windows.ps1:247 — the sweep deletes *every* `hermes-update-ui-*` directory under $TempDir, justified by the in-progress marker serializing hand-offs — but that marker serializes within one HERMES_HOME. Two independent installs (different homes) updating concurrently will each consider the other's live profile dir "stale"; Windows file locking makes the delete mostly no-op for in-use files, but partial deletion of a sibling run's profile is possible noise. Cheap hardening: skip dirs whose name ends in the current $PID complement... more simply, only sweep entries older than e.g. 24h (`LastWriteTime`), which still clears interrupted leftovers without touching a concurrently running peer.

No blocking issues found.
