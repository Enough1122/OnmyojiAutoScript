> AI code review — automated review for reference; please use your judgment.

- docker/SOUL.md:1 / hermes_cli/default_soul.py:10-13 — Nit: the new sentence is now hand-duplicated across two copies that must stay textually identical (the Docker image's SOUL.md vs. `DEFAULT_SOUL_MD`, the template seeded into HERMES_HOME), and nothing in this PR or the visible test suite asserts their parity — past drift would go unnoticed exactly like this sentence could. Why it matters: persona changes silently diverge between Docker and CLI installs. Suggestion: derive docker/SOUL.md from `DEFAULT_SOUL_MD` at image build time, or add a one-line parity test comparing the files' text. The added guidance itself reads clearly and sits sensibly in both flows.

_— hermes-week-review automated review (reviewer-d)_

No blocking issues found.