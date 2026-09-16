> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Correct semantic restoration per the documented contract (0 = show full paths/commands), and the added `_cap > 0` guard in run.py is a genuinely important catch — under the old falsy-coalescing the unlimited case would have sliced `len-3` characters off every preview.

- **Negative values are now silently "unlimited."** The old code coerced anything non-positive to 40; the new code only special-cases None, so a config typo like `tool_preview_length: -1` disables truncation entirely instead of erroring or falling back. Suggest normalizing (`cap = 40 if _pl is None else max(0, _pl)`) so the documented domain stays {n>0 = cap, 0 = unlimited}.

- **No tests for either site**, despite this being a documented-contract behavior change; one parametrized case per value class (unset → 40, 0 → untruncated, 5 → truncated with ellipsis, and the negative case once point 1 lands) would lock it.

- **Verify parity at the base.py site:** run.py got the `_cap > 0` truncation guard, but base.py hands `cap` straight into `prepare_tool_preview` — confirm that helper itself treats cap <= 0 as unlimited rather than slicing, or apply the same normalization before the call.

Nit: the "Local patch 2026-08-20" annotations read like carry-over provenance markers rather than rationale; keeping just the why (0 means unlimited per config docs) would age better in git history.

No blocking issues found.