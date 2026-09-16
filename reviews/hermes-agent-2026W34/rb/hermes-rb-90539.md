> AI code review — automated review for reference; please use your judgment.

Right call treating curation as prioritization rather than a filter, and the companion guard in `detect_provider_for_model` is the necessary second half — with hundreds of tool-capable slugs live, bare-name collisions against `custom:` endpoints become common, and the new tests pin both bare `custom` and `custom:*`. Items:

- hermes_cli/models.py:2036 — issue (verification) — appending every tool-capable live model can add several hundred picker entries; confirm the picker surface that consumes this list renders/searches it acceptably (virtualized or filtered), since this function also feeds anything that embeds the full list verbatim — why it matters — a picker that renders 400 rows unpaginated turns the improvement into a UX regression on slow terminals.

- hermes_cli/models.py:3460 — nit — the custom-provider early return now also bypasses the *curated* Step-2 match that previously could resolve an exact slug; that's the intended hardening, but it means a user who deliberately points a custom provider at an OpenRouter-hosted model loses auto-slug resolution — worth one line in the PR description stating that trade-off is deliberate.

No blocking issues found.

— reviewer-b (automated review)
