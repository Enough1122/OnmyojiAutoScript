> AI code review — automated review; please use your judgment.

Exactly the right fix for an agent-facing UX trap: computing `categories` from the **unfiltered** set means a missed category filter now returns the full category list plus an explicit "this does not mean the skill is missing — retry without the filter" message, while hits stay clean (no spurious warning). The hub-side additions are equally good — distinguishing "installed locally, hub doesn't offer it" (with the on-disk path and a pointer to `skill_view`) from a genuine not-found kills the second measured failure mode where users concluded an installed skill didn't exist. Both behaviors are pinned by tests including the negative ("a hit carries no warning").

No blocking issues found.

Nit (`hermes_cli/skills_hub.py` `_find_local_skill`:~866–880): if two categories contain a skill with the same bare name, the first match wins arbitrarily and the printed path may point at the other one; returning all matches (or preferring exact category when the identifier carried one) would make the hint precise — cosmetic, since it's only used to say "it's installed somewhere".

— reviewer-a · automated agent review (Hermes week-review)
