> AI code review — automated review for reference; please use your judgment.

- optional-skills/research/hydrafetch/SKILL.md:96+ — Nit: none of the curl examples set `--max-time`; every other operational concern (credits, retries, politeness) is covered, but an agent running these verbatim on a stalled origin will hang the terminal tool until its own outer timeout. Why it matters: this skill's whole procedure section is copy-paste-ready by design, and one hung call is the most common real-world failure mode of hosted scrape APIs. Suggestion: add `--max-time 60` (or similar) to the canonical examples.

- Same file — Positive: exemplary agent-facing documentation for an optional paid skill — honest cost framing with a per-endpoint credit table, free alternatives listed *before* usage, fetched-content-treated-as-data warning, explicit don't-retry guidance for 400/422/402, source-attribution procedure, and a working verification snippet. Frontmatter matches the optional-skills contract, and all three `related_skills` references resolve to real sibling skills (research/scrapling, research/duckduckgo-search, research/domain-intel).

_— hermes-week-review automated review (reviewer-d)_

No blocking issues found.