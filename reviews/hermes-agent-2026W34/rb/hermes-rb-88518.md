> AI code review — automated review for reference; please use your judgment.

Review of "test(tui): stabilize profile-local MCP discovery probe". Legitimate flake fix: the probe spawns a real MCP subprocess whose discovery latency on loaded CI runners exceeds the old fixed waits, and both the per-profile config timeout and the response queue wait are raised with comments explaining that this test verifies discovery, not the production latency bound. No blocking issues found.
