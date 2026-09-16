> AI code review — automated review for reference; please use your judgment.

*(Note: an identical copy of this diff appeared earlier under #89140, where my full review landed before that PR was recycled/closed; reposting verbatim here so the live PR carries it.)*

Well-factored addition: `_apply_aux_choice_to_all` deliberately reuses `_save_aux_choice` per slot so delegation's empty-provider convention and per-task `timeout`/`extra_body` preservation behave identically to the single-task flow — and the tests pin exactly those two hazards (`test_apply_aux_choice_to_all_preserves_timeouts`, plugin-task inclusion), plus the `mixed` summary logic and the new menu entry. The custom-endpoint flow handles every interrupt path cleanly.

No blocking issues found.

Nit: "set everything to auto" now has two implementations that must stay equivalent — the menu's `__auto__` branch calls `_reset_aux_to_auto()`, while `_apply_aux_choice_to_all(provider="auto")` reaches the same state through the per-slot save path (`test_apply_aux_choice_to_all_auto_resets` exercises only the latter). They agree today, including delegation handling, but any future change to one silently diverges the other — consider making the menu branch call `_apply_aux_choice_to_all(provider="auto", ...)` so a single owner defines auto-reset semantics.

— Reviewed by Hermes AI reviewer (reviewer-f2)
