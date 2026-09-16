> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean additive surface change: `cache_read` rides the existing `_get_usage` getter pattern and is typed optional in the desktop contract with an explicit "absent on older backends" note, so mixed-version deployments degrade to undefined rather than breaking. Nothing else consumes it yet — presumably a follow-up wires the UI — but as a plumbing PR this is exactly the right shape.
