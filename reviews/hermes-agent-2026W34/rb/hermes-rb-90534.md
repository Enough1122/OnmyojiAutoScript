> AI code review — automated review for reference; please use your judgment.

Well-scoped feature with an unusually disciplined test set: the load-bearing contracts (propose-before-save, dedupe requirement, noise bar, honest empty result) are each pinned by a dedicated test, and the dispatcher-wiring tests guard against exactly the "registry entry exists but nothing routes" failure mode. Items:

- agent/upskill_prompt.py:17 — nit — imports the underscore-private `_AUTHORING_STANDARDS` / `_SOURCE_HYGIENE` from `learn_prompt`; cross-module private imports mean a /learn refactor can break /upskill invisibly — suggestion — rename them public (`AUTHORING_STANDARDS`) in learn_prompt or move both to a shared `skill_standards.py`.

- docs/design-upskill.md:3 — nit — ships with `Status: proposed` inside the very PR that implements it; update to reflect reality (or drop the file) so future readers don't wonder whether the feature actually landed.

- gateway/run.py:17245 — nit (coverage) — the gateway branch mirrors the CLI one but has no test asserting `event.text` is rewritten to the sweep prompt while preserving fall-through; the CLI side got sentinel-based tests — parity would protect against someone "cleaning up" the mutation later.

No blocking issues found.

— reviewer-b (automated review)
