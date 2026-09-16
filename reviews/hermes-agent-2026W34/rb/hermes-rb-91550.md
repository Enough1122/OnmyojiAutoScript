> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Clean fix for a real packaging gap: Hub installs ship only SKILL.md-referenced support files, so the helper import and the rationale doc previously vanished in profile installs. The new regression tests are exactly right — one pins the referenced-path extraction against the expected set, and the stronger one simulates a real subset install (copying only referenced files into a fresh HERMES_HOME), evicts any cached \`_hermes_home\` module, executes the installed \`sources.py\` by spec, and verifies both the profile-scoped ledger resolution and an actual ledger write. A typo'd reference would fail the copy step, so even path drift is implicitly covered.

Nit: tests/skills/test_grounded_citations_hub_package.py imports the private \`tools.skills_hub._referenced_support_paths\`; fine for an in-repo regression test, just noting the coupling so a rename there updates these tests deliberately rather than by surprise.

No blocking issues found.