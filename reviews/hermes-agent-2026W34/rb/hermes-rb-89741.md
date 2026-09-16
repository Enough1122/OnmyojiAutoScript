> AI code review — automated review for reference; please use your judgment.

Clean separation of concerns: provider-authored `summary` text now survives as its own field instead of being conflated with the `text` fallback, and the regression test pins exactly the shape that used to lose it (tool-call turn, empty content, explicit summary). Items:

- agent/codex_responses_adapter.py:1647 — issue (verification) — this PR *produces* `codex_reasoning_summary` but the visible hunks contain no consumer; if the interim-commentary surfacing lives in a companion change, fine — otherwise the field is dead weight and the bug isn't actually fixed end-to-end — suggestion — link the consumer PR/commit in the description and add one assertion at the surfacing site (e.g., the interim callback fires with the summary on a content-empty tool-call turn) so the chain is proven, not assumed.

No blocking issues found — item 1 is about proving the last mile.

— reviewer-b (automated review)
