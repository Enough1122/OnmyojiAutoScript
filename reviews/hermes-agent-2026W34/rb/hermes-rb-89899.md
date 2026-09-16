> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Well-authored optional skill: description fits the 60-char budget and house style, all seven canonical sections are present, the When-to-Use/Don't-use split is crisp, and the Pitfalls section is genuinely operational (fest-next cwd requirement, phase gates being human-only, the hermes -z working-directory trap, docker image gaps, .hermes.md outranking AGENTS.md). The explicit "do not run fest workflow approve on your own work" boundary is exactly the right instruction for an agent-driven execution loop.

Two small points:

- **related_skills: [subagent-driven-development]** - please confirm that skill exists in this repo's tree; per the project's own authoring rules, dangling related_skills entries are a known hygiene issue.
- **Prerequisites offer `curl ... | bash` from the repository's main branch** as an install path. For a skill an agent may execute at install time, pinning the URL to a tagged release (or at least noting the trust implication) would be more defensible than a mutable-branch pipe-to-shell.

Nit: SKILL.md says the tap "publishes 12 skills," a count that will drift; pointing at the tap README without the number ages better.