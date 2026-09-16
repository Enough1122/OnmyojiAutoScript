> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct edge-case handling with the failure documented precisely: an `external_dirs` entry that *is* the skill package made `relative_to(root)` yield `"." `, which is neither a valid `skill_view()` name nor dispatchable as `/<skill>`. Returning the package directory name — the same identifier discovery registered it under — is the right identity, and the test pins both the new behavior and that parent-dir layouts still produce nested paths.
