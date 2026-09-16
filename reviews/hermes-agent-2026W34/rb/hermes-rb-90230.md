> AI code review — automated review for reference; please use your judgment.

Review of "fix(github): preflight repository-object authority". Major hardening of the publish flow: authority is verified BEFORE each mutation class (PR-create on target, contents+refs on fork), every previously fire-and-forget HTTP call now checks status and validates its payload shape (repo/branch regexes, commit SHA, PR URL), failures become typed capability errors with preserved 403 evidence, and publication requires a receipt with commit + verified diff. The capability test matrix (authority separation across operation classes, installation-vs-PAT contexts, branch-protection distinctness) is exactly what a trust-boundary module needs. Suggestions:

1. hermes_cli/skills_hub.py:1690 (branch-name reuse) — `add-skill-{skill_name}` collides on any republish, now surfacing as a typed 422 instead of silently proceeding; consider reusing/updating an existing publish branch (or suffixing a timestamp) so the second publish of one skill doesn't require manual fork cleanup.

2. hermes_cli/skills_hub.py:1688 (unsanitized slug) — `skill_name` flows into the git ref unvalidated; a name with spaces/slashes guarantees the typed 422 — normalize to `[a-z0-9-]` up front so valid skills don't hit the failure path at all.

3. hermes_cli/skills_hub.py:1745 (partial-upload orphans) — sequential contents uploads mean a mid-loop failure leaves half the files committed on the fork branch; pre-existing, but now that every step is authority-checked it's the remaining rough edge — either delete the orphan branch on failure or resume from `last_commit_sha` on retry.

4. hermes_cli/skills_hub.py:1646 (legacy auth fail-closed) — the AttributeError catch correctly refuses to mutate when preflight is unavailable, but the message should tell the operator WHAT to upgrade ("update the GitHub auth provider to a capability-aware version") — "unavailable" alone reads like a transient fault.

No blocking issues found.
