> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): preserve gateway when switching profiles". Right fix: routing profile switches through `ensureGatewayAgent(connectionId, target)` keeps the live registry-backed connection instead of spawning a parallel per-profile gateway, with a clean fallback to `ensureGatewayProfile` when there is no registered source, and a regression test pins exactly that precedence. Suggestions:

1. apps/desktop/src/store/profile.ts:508 (duplication) — `selectProfile` and `newSessionInProfile` now carry byte-identical three-line connection-resolution blocks; extract a small `ensureGatewayForSwitchedProfile(target)` helper so the next caller can't pick the wrong branch.

2. tests/store/profile-agent-activation.test.ts (coverage symmetry) — only selectProfile's registry-preserving branch is tested; add the twin assertion for `newSessionInProfile` plus one null-$connection case pinning the fallback to `ensureGatewayProfile`, so both entry points stay locked to the intended routing.

No blocking issues found.
