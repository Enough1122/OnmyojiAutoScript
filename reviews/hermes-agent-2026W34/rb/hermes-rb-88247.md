> AI code review — automated review for reference; please use your judgment.

Excellent catch on a genuinely subtle bug: clearing `summary_model` meant "use main model" to the fallback code but meant "re-resolve `auxiliary.compression`" to `call_llm` — so the retry silently re-called the model that just failed, and the no-second-fallback rule then aborted compression entirely. The fix names the main runtime explicitly through one shared route helper applied at both entry points, clears the stale auth/quota flag so a successful main retry isn't aborted by the aux failure, and — best of all — updates the three pre-existing tests whose assertions had *pinned the broken behavior* ("model not in kwargs"). The new suite covers quota-exhausted fallback, flag non-stickiness, pre-fallback route preservation, no-aux-config passthrough, and the micro path.

— reviewer-b (automated review)

No blocking issues found.
