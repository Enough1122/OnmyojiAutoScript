> AI code review — automated review for reference; please use your judgment.

Two loosely-related changes ride together here:

1. `plugins/memory/honcho/session.py` — good fix with a proper test: when a peer_perspective-filtered search silently returns empty (self-hosted builds without a filterable column), the new peer_id-filter retry recovers results, and the old peer-search fallback remains as the last resort. Assertions pin both the fallback order and the exact filters used per attempt. One nit: three nested fallback levels inside one method is getting deep — a small ordered list of strategies would read flatter, but functionally it's correct.

2. `tools/opencode_serve_tool.py` + toolset/skill/docs — well-documented new integration (server-side execution clearly called out, credentials scoped to profile env and scrubbed from children, graceful ReadTimeout guidance pointing at `opencode_status`). Two gaps worth addressing:
   a. `_save_sessions` writes the JSON session map non-atomically (````write_text````); a crash mid-write truncates the store and every project→session mapping is silently lost (the code already treats that as recoverable, but the repo has `utils.atomic_write_text` used everywhere else for exactly this) — suggestion: use it.
   b. No tests cover the new module: `_text_from_parts`, `_diff_summary`, and the run/status happy paths are pure enough to test with a mocked httpx client the way other tool tests in this repo do — right now the 320-line tool ships with zero coverage while its sibling fallback fix got some.
   
3. Nit (`tools/opencode_serve_tool.py` `opencode_run`:~): a blocking `timeout_minutes=30` default means the tool can hold a worker for half an hour; consider documenting the interaction with the executor's own tool deadline in the schema description so a model doesn't choose 30 minutes casually.

Note re scope: this PR adds an `opencode serve` delegation toolset (remote coding-agent backend), which is unrelated to the separate `opencode2` tree — flagging only because the names are confusable.

— reviewer-a · automated agent review (Hermes week-review)
