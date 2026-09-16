> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Textbook fix: the deferral branch used to answer \`confirm_required=False\` without consulting the selection guards, so consent-capable clients never prompted and the pick was dropped one turn later when \`_apply_pending_model_switch\` ran the same guards against the stashed unconfirmed flag. Running the pre-resolution guards *before* stashing, requiring the ack to survive into the stash entry, and failing open on a broken guard (with the apply-time check kept as backstop) closes the loop correctly. The test module's four classes map exactly onto the behavioral matrix — guarded/unguarded × confirmed/unconfirmed, plus the guard-crash fallback and the helper contract — and the docstring honestly documents the under-fire-only limitation of early guarding.

Two small observations:

- **Clients that ignore \`confirm_required\` now lose the pick outright.** Previously an unguarded-client user saw the pill move and then revert next turn (confusing but visible); now nothing is stashed, so the switch just doesn't happen with no visible trace unless the client surfaces \`confirm_message\`. That's the more honest failure mode, but consider documenting it for client authors, or echoing the previously-live model in the response so a smart client can render what would change if confirmed.

- **tui_gateway/server.py:~12022 — the response carries both \`warning\` and \`confirm_message\` with identical content.** Presumably one is legacy compatibility; a comment naming which field clients should read would prevent divergence later.

Nit: \`TestHelperContract\` could also pin that an explicit \`--provider\` reaches \`combined_selection_warning\`, since provider-keyed guards are called out in the docstring but only the model-id path is asserted.

No blocking issues found.