> AI code review — automated review for reference; please use your judgment.

Review of "feat(mcp): add Respira (WordPress) to the MCP catalog with a curated 25-tool default". Exemplary manifest hygiene: exact version pin per the supply-chain contract, per-tool curation with token-budget math (~250 tools ≈ 150k tokens justifies it), destructive site-admin surfaces excluded by default with named opt-in, snapshots/undo documented, and the stdio-vs-per-site-OAuth trade-off argued rather than assumed. Suggestions:

1. optional-mcps/respira-press/manifest.yaml:139 (default tier mixes reads and LIVE WRITES) — the cration rationale is token-cost, not risk, so `respira_update_page`, `respira_build_page`, `respira_update_element`, media upload/sideload all ship ENABLED for a fresh install — an agent holding a full-access config value can mutate production pages with zero extra consent, while the destructive-admin tier was deliberately held back; consider a read-only default tier (orientation + read + snapshots) with writes behind `hermes mcp configure`, mirroring how this very manifest treats `respira_update_core_security`.

2. manifest.yaml:120 (offline unverifiable tool names) — the 25 names can't be validated against the server's tools/list at review time, and a typo silently disables a tool instead of failing loudly — confirm install-time verification reports unknown `default_enabled` entries as warnings/errors, especially since every vendor bump PR (which you've committed to sending) reshuffles this list.

3. manifest.yaml:78 (nit, blast radius) — one `RESPIRA_CONFIG_B64` carries every site on the account, so a leaked value exposes the whole fleet; the post_install covers read-only tiers well — add one sentence recommending per-scope values for shared machines.
