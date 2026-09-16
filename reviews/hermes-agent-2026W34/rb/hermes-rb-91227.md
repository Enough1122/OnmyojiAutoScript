> AI code review — automated review for reference; please use your judgment.

Good shape: retiring the tab through the *registered* closer (instead of the old bare `$groupChatWorkspace.set(null)`, which left the main tab orphaned) fixes both the stale surface and the selection, the local-vs-remote split is deliberate and tested from both entry points, and the close-before-open ordering is asserted rather than assumed. Suggestions:

1. apps/desktop/src/plugins/hermes-bots/plugin.js:5048 — dismissal happens before the async canonical open, but nothing restores the group tab if `openBotCanonicalChat` then fails (backend down, session create error). The user ends up with neither surface — strictly worse than the old bug for that path. Consider capturing the closer result and re-seating the group tab (or surfacing an error affordance) when the open rejects.
2. plugin.js:9567 (`closeGroupChatMainTab`) — retiring the tab destroys any unsent composer draft in that group with no confirmation. If drafts aren't persisted elsewhere, even a lightweight "group chat has unsent text" guard (or preserving the draft keyed by group id) would prevent silent loss on a stray bot click. If drafts already survive tab retirement, ignore this.
3. Behavior change worth a release-note: previously clicking a REMOTE bot also cleared `$groupChatWorkspace`; now remote opens touch nothing (stay-and-@). The tests pin this intentionally — just make sure it's intended product behavior, since users relying on "clicking anything clears the group selection" will see a difference.
4. tests/group-to-local-bot-handoff.test.mjs:26 — the vm loader strips SDK/react imports by regex and stubs ~40 UI symbols; every rename in plugin.js silently degrades this suite to false-pass territory (same fragility as the other vm-based suites in this plugin). Acceptable given the pattern is established, but the e2e spec is the real safety net here — keep it green in CI. (nit)

No blocking issues found.
