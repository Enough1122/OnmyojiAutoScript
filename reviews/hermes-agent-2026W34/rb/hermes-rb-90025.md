> AI code review — automated review; please use your judgment.

The fix targets a genuinely harmful misattribution: an in-process child's small iteration cap (`16/16`, `50/50`) was advancing the *dispatcher worker's* failure breaker and archiving healthy parent tasks, and the five-case matrix exercises all four contexts (worker fires, delegate child skips, `_persist_disabled` fork skips, non-dispatcher cron skips) plus a unit truth table — with real incident IDs cited as motivation.

1. `agent/turn_finalizer.py:~108–128, ~230–236, ~246–249` — three comments read ````"LOCAL PATCH 14 …"````, narrating deployment patch provenance rather than describing behavior for upstream reviewers — why it matters: same issue as #90578's "local patch" hunks; it obscures which repo state this applies to and reads as though a private fork leaked into the PR — suggestion: reword to state the rule ("budget-exhaustion recording is dispatcher-owned only") and drop the patch numbering.

2. Nit (`:~120–124`): gating on ````getattr(agent, "_persist_disabled", False)```` couples the decision to a persistence flag set by `background_review.py`; if that attribute is renamed or its meaning broadens, review forks silently start counting against parents again — suggestion: introduce an explicit marker (e.g. `agent._budget_attribution_exempt = True`) owned by the fork setup, or at least reference the setting site in the docstring so rename tooling can follow it.

— reviewer-a · automated agent review (Hermes week-review)
