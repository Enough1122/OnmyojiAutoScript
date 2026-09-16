> AI code review — automated review for reference; please use your judgment.

Well-judged loop breaker: the streak is computed inside the same transaction as the transition (no TOCTOU), distinct feedback provably resets it (dedicated test), `0` disables while negatives raise, the trip lands in `blocked`/`needs_input` where the existing unblock-loop breaker can't be re-triggered by cron, both `review_loop_detected` and the synthesized `blocked` events carry full attribution payloads, and the rework-context change — foregrounding the latest correction above the task body, explicitly labeled as instruction-not-context, surviving crash retries — fixes the *cause* of these loops (the correction was buried in bounded history), not just the symptom. Config knob is documented in the settings table and event catalog.

1. `hermes_cli/kanban_db.py:~6740–6747` — "same correction" is exact string equality after `.strip()`; a reviewer model that varies case, punctuation, or phrasing (````"Fix the boundary."```` vs ````"fix the boundary"````) never trips the breaker, and neither does an alternating A/B/A/B correction pair — why it matters: LLM reviewers are exactly the kind of writers that paraphrase every round, so the protection may silently not engage in the noisiest real cases — suggestion: at minimum `casefold()` + whitespace-collapse before comparing (cheap, still conservative); consider documenting that semantic paraphrases are out of scope.

2. Nit (`:~6800–6822`): `review_loop_detected` is immediately followed by a synthetic `blocked` event carrying overlapping information; fine, but add one sentence to the event-catalog doc row stating the ordering guarantee (same transaction, detected-then-blocked) so event consumers don't treat them as independent incidents.

3. Nit: the ````cfg_get(load_config(), "kanban", "repeated_review_changes_limit", ...)```` stanza is duplicated verbatim between `kanban.py` and `tools/kanban_tools.py` — a one-line helper would keep default and key in one place.

— reviewer-a · automated agent review (Hermes week-review)
