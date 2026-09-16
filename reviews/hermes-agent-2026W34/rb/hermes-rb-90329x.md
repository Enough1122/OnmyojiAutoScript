> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Accurate and useful documentation correction: the old text promised SSH sources are "inventoried without spawning anything" *persistently*, which contradicted the actual connect-on-demand behavior for both SSH and the local runtime when a remote gateway is primary. The rewrite states the real lifecycle precisely — local bots appear once a local backend is live, persist for the session, and hide again after restart — in both bot-mode.md and multi-connection-desktop.md, with consistent wording between the two pages. Docs-only, no code impact.
