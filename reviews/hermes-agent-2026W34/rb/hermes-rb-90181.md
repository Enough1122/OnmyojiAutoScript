> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): isolate pooled profile backends". Tight change: `serveBackendArgs` becomes the single source of the pooled-backend invocation (main.ts stops hand-rolling the array — nice dedup side effect), `--isolated` rides only on profile-pooled spawns, and the legacy dashboard fallback strips the serve-era flag with the reasoning documented inline. Tests updated on both command shapes. Suggestions:

1. apps/desktop/electron/main.ts:10073 (runtime capability gating) — the strip only covers the LEGACY dashboard fallback; if any intermediate runtime class supports `serve` but predates `--isolated`, the flag would be an unrecognized argument and the pooled backend fails to start after auto-update — worth confirming that every runtime classified as "serve-capable" also accepts `--isolated`, or gating the flag on the same capability signal that picks serve-vs-dashboard.

2. nit — `dashboardFallbackArgs` filters EVERY `--isolated` occurrence from the tail, including one a user deliberately supplied through extra-args config; harmless today given the flag's newness, but a first-occurrence-only removal (or comment acknowledging it) would keep intent explicit.
