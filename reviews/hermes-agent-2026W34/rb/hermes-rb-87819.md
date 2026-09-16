> AI code review — automated review; please use your judgment.

Correct surface-specific fix with the trade-off spelled out: on the xterm.js dashboard any active mouse protocol kills text selection entirely, so `applyDisplay` now forces tracking off there regardless of config, while native terminals keep the full config-driven presets. The getter-based env mock (hoisted mutable flag over the load-time-evaluated module) is a clean way to make the once-computed constant testable, and all four cases — dashboard default, dashboard overriding an explicit "all", native default, native presets — are pinned.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)
