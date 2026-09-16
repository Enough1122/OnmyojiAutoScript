> AI code review — automated review for reference; please use your judgment.

Review of "fix(web): preserve website-policy blocked extract results during rescue". The tested behavior is right — policy refusals are intentional outcomes, not failures, so `_rescue_extract` partitions them out (`_policy_blocked_result`) and preserves them verbatim while the keyless ring rescues only genuine backend errors; the two new tests pin both the blocked-only skip (failover not called) and the mixed case (ring receives just `ok.test`). Two observations:

1. scope/labeling — the PR's diff is TEST-ONLY: the `_policy_blocked_result` partition already exists at the head of the branch (and, presumably, on the base), so nothing here changes runtime behavior — please confirm the implementation truly landed on the base branch (otherwise these tests fail CI), and consider retitling to "test(web): ..." so the changelog doesn't record the fix twice.

2. tools/web_tools.py:540 (defensive path contradicts the policy invariant) — when provider result order breaks parity (`len(results) != len(urls)`), the fallback sets `rescue_idx = ALL results`, which re-fetches POLICY-BLOCKED urls through the keyless ring — exactly what the docstring promises never happens ("entries flagged by _policy_blocked_result are never re-fetched") — the scenario requires an already-broken provider response, but a policy bypass landing inside that defensive branch is worse than skipping rescue; prefer filtering blocks by URL match even under parity loss, or bail out without rescuing at all.

No blocking issues found beyond item 2 being worth a deliberate decision.
