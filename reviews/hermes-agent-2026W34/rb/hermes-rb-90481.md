> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Deliberate prompt-policy rebalance, executed cleanly: discovery stays broad ("err on the side of loading," partial-relevance trigger kept, the \`hermes-agent\` self-configuration exception intact), while the two autonomous side-work mandates (patch broken skills unprompted; offer to save every difficult task as a skill) are replaced by an explicit do-not-do-side-work guard. Developer docs example is synced, and the regression test pins both the new phrasing and the *absence* of the old skill_manage instruction — asserting on absence is exactly right for a prompt-tuning PR.

Nit: dropping the "offer to save as a skill" nudge will measurably reduce how often users are prompted to capture workflows into reusable skills — presumably the intent, but since it changes observable agent behavior for every session, a line in the release notes ("skills are no longer proactively offered or patched mid-task") would keep expectations aligned.

No blocking issues found.