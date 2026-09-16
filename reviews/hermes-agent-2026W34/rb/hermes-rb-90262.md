> AI code review — automated review for reference; please use your judgment.

No blocking issues found.

Nit: complete_task now fetches the task once for the pre-checks (status/expected_run_id/metadata gate) and the main write transaction presumably re-validates — a second read of the same row. Harmless at kanban scale, but if the early reads ever drift from the in-transaction ones (they must stay identical or completions start failing/succeeding asymmetrically), this is the seam to watch. The opt-in design itself is right: legacy NULL keeps unrestricted completion, null values count as present (explicit "none found"), rejections emit an auditable event BEFORE raising without mutating state, the worker context tells the model the contract up front including the null escape hatch, and every surface (CLI create/complete, tool schema, dashboard single+bulk with a proper 409) handles the new error consistently — all pinned by tests including the migration regression and the terminal-state no-event-duplication case.

— Reviewed by Hermes AI reviewer (reviewer-f)
