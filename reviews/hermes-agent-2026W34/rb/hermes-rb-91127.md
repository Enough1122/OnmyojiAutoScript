> AI code review — automated review for reference; please use your judgment.

Deliberate policy flip from "err on the side of loading" to minimal triggered loading; the router-first rule and the `hermes-agent` self-config carve-out survive, which preserves the two cases where over/under-loading hurt most. Items:

- agent/prompt_builder.py:2170 — issue (behavioral risk) — the new gate ("topical overlap or possible usefulness is not enough") will under-trigger on tasks whose phrasing doesn't match a description's concrete scope, and unlike over-loading, misses are silent: the user just gets a worse answer with no signal — why it matters — this trades a context-cost problem for a recall problem, and nothing in the diff measures either side — suggestion — before/after this lands, run one of the tree's eval harnesses (or even an ad-hoc 20-task set) comparing task-success with old vs new guidance, and note the result in the PR description so the trade-off is a data point, not a vibe.

- tests/agent/test_prompt_builder.py:284 — issue — the test asserts nine long verbatim sentences from the guidance prose — why it matters — any future copyedit ("don't" → "do not", reordering) breaks the suite despite unchanged semantics, training maintainers to blindly update assertions — suggestion — pin the stable anchors instead (`"## Skills (selective)"`, presence of the four operative rules via short distinctive substrings like `"one primary skill"`, plus the two absence checks for the old policy), or accept the coupling consciously and say so in a comment.

- agent/prompt_builder.py:2186 — nit — the removed trailing line's intent now lives mid-paragraph as "If no description directly matches, proceed without loading a skill"; consider keeping it as the final sentence after `</available_skills>` too, since placement at the end is where a model weighing whether to load actually looks.

No blocking issues found — item 1 is a product call worth having made explicitly with numbers.

— reviewer-b (automated review)
