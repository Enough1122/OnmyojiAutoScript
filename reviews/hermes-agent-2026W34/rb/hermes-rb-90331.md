> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Disciplined tool design: strictly a thin wrapper over the CLI's own profile primitives, off unless the `profiles` toolset is opted into, invisible to delegated children, fail-closed on unreadable config, classified mutating for guardrails, and — importantly — **no delete action**, keeping destruction behind interactive confirmation flows. Validation covers traversal (`../escape`), reserved/built-in names, soul size caps rejected *before* any directory exists, and clone/no-skills conflicts caught pre-creation. The 255-line test file even pins the schema-enum/handler-action match, which most tool PRs forget. Findings below are minor:

1. tools/profile_manager_tool.py (schema description) — worth one sentence in the tool's description telling the model what a freshly created profile does **not** have: no credentials, no provider/model config, no running gateway. Agents asked to "spin up a bot" will otherwise create profiles and then be surprised when the first chat can't reach a provider; stating the next manual step (configure credentials via CLI/desktop) sets correct expectations inside the model's own planning.
