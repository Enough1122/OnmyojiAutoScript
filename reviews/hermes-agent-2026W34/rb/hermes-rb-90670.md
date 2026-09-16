> AI code review — automated review for reference; please use your judgment.

Right fix for an unhandled-rejection crash path: open stays hands-off on failure while close degrades gracefully to closing by the raw target string, which preserves the user-visible behavior that matters (the preview actually closes). One structural concern:

1. apps/desktop/src/app/session/hooks/use-preview-routing.test.ts:12 — the suite **inlines copies** of both call-site bodies instead of exercising `use-preview-routing.ts` itself ("inline the logic under test"). The copies will drift: rename a variable or change the candidate list in production and these tests keep passing against stale logic. Either extract the two routings as pure exported helpers (`openPreviewRouting`/`closePreviewRouting`) that the hook calls, and test those directly, or drive the hook with `renderHook`. As-is this is coverage theater.
2. use-preview-routing.ts:106 — the open-path catch is fully silent; a `console.debug` with the error makes "why didn't my preview open" diagnosable from the devtools console at zero cost.
3. Close path detail worth confirming: when `normalizeOrLocalPreviewTarget` resolves but `reachablePreviewUrl` rejects *inside* the then-block, the same catch runs and closes by raw target only — the already-resolved candidates are dropped. Probably fine (normalization succeeded, reachability failed ⇒ the resolved url is dead anyway), just noting the coupling so it's a decision rather than an accident. (nit)

No blocking issues found.
