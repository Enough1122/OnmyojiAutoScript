> AI code review — automated review for reference; please use your judgment.

Right UX distinction with both sides tested: completed edits mount collapsed, in-flight edits keep the streamed diff visible so progress isn't hidden, and the click-to-expand path is asserted through real DOM attributes rather than store internals. One verification:

- apps/desktop/src/components/assistant-ui/tool/fallback.tsx:373 — issue (verification) — the tests cover mount-time defaults but not the *transition*: an edit that streams open (`defaultOpen` effectively true) then completes flips `defaultOpen` to false — whether the row actually collapses depends on `useDisclosureOpen` re-seeding on default change or honoring first-seed-wins — why it matters — if it re-seeds, a diff the user was reading snaps shut mid-review; if first-seed wins, completed edits that streamed stay expanded forever, quietly contradicting the PR title for the most common live flow — suggestion — add one test rendering pending-then-completing and pin whichever behavior is intended.

No blocking issues found.

— reviewer-b (automated review)
