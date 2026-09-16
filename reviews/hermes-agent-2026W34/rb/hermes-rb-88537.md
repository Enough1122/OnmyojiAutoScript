> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): run repo discovery server-side in remote mode". Correct architecture: the Electron crawl can only see the app host's filesystem, so in remote mode discovery must run on the backend that holds the repos — implemented as a `projects.scan_repos` RPC with a bounded server-side walker (depth limit, junk/hidden exclusion, .git+HEAD validation), generation-guarded client state, and a solid structural-contract test file (nested repos, depth bounds, junk/hidden skipping, disabled no-op, fake-.git rejection). Suggestions:

1. tui_gateway/methods_config.py:109 (event-loop blocking) — `repo_scan.scan_repos` is a synchronous filesystem walk invoked from the RPC handler; if this method dispatcher executes handlers on the event loop rather than a worker pool, a large policy root freezes ALL gateway traffic for the duration of the crawl — confirm the dispatch model off-loads sync handlers, or wrap the scan in `asyncio.to_thread`.

2. nit — the client sends `discovery_policy` in the request while the server resolves its OWN policy via `_repo_discovery_policy()` and ignores the payload; either honor the client's policy (with server-side clamps) or drop the field so the contract doesn't imply client control over backend scanning.
