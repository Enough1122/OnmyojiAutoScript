> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): open active bot sessions from Active now". Right fix for a real routing bug: chips now open the human-facing session that produced the activity signal (resolved lineage tip honored), fall back to the canonical chat when there is no live human session or it is definitively gone, and deliberately surface transient hydration failures instead of dumping the user in Home. Error triage in `openActiveBotSession` and the pure `activeHumanSession` window helper are both cleanly tested. Suggestions:

1. apps/desktop/src/plugins/hermes-bots/plugin.js:3397 (error-string coupling) — the fallback decision hinges on `/session not found/i` matching a human-written message from `host.openSession`; if upstream ever rewords it ("unknown session", "no such stored session"), stale-chip clicks start THROWING at users instead of falling back to the canonical chat — prefer matching a structured error code/cause if the SDK offers one, or broaden the matcher and add a shared constant so plugin.js and tests can't drift.

2. apps/desktop/src/plugins/hermes-bots/tests/active-now-session.test.mjs:8 (slice-extraction fragility) — loading the function by `indexOf('async function openActiveBotSession(')` plus the next-section comment anchor means renaming the section header silently empties the extracted slice (the notEqual assertions catch it, good), but three test files now each carry near-identical vm-slice loaders — consider a tiny shared test helper that loads named functions once, so boundary renames get fixed in one place.

3. apps/desktop/src/plugins/hermes-bots/plugin.js:9940 (generation race nuance) — the staleness check runs only after the FIRST attempt resolves: if the roster regenerates while `openActiveBotSession` is awaiting hydration, a successful open still returns through the stale path (fine), but a null result correctly falls through to canonical — worth one comment noting the intent, since future readers often "fix" this ordering and accidentally double-open.

No blocking issues found.
