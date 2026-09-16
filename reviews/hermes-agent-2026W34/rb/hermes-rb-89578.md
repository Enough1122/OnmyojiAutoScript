> AI code review — automated review for reference; please use your judgment.

Right consolidation: the hand-rolled rAF machinery (visibility/blur/focus listeners, pause flag, fps throttle, force-invalidate) duplicated exactly what `createBudgetedLoop` already owns, and delegating removes ~60 lines of easy-to-drift lifecycle code while gaining the observability pause controller for free. One behavioral delta to verify and two nits:

1. star-map.tsx:~610 — the old code had an explicit **force path**: interaction (hover/focus/scrub) set `force = true`, bypassing the 30fps cap for an immediate repaint. The new `invalidateRef` only sets `dirty`, so interaction-driven repaints are now throttled to the loop cadence — worst case ~33ms extra latency on hover/scrub feedback. If `createBudgetedLoop` exposes a priority/urgent frame, use it here; otherwise confirm the added latency is acceptable for this canvas before merging.
2. On wake from the paused state, the old code forced `dirty + immediate frame`; per the new comment the loop "picks it up on its next frame" — fine at 30fps, but confirm the pause controller marks dirty on wake (or that a stale pre-pause frame for one tick is acceptable). Likely imperceptible; noting for completeness. (nit)
3. No test pins that StarMap actually runs on the shared loop; given this repo's source-contract test convention, a one-line assertion would stop a future revert to hand-rolled rAF from going unnoticed. (nit)
4. `loop.dispose()` replacing four add/removeEventListener pairs is exactly the cleanup simplification this kind of extraction should produce. (positive)

No blocking issues found.
