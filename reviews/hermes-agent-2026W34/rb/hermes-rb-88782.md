> AI code review - automated review for reference; please use your judgment.

Reviewed the diff. Clean surface wiring: the Kill button reuses the TUI's existing `subagent.interrupt` gateway RPC (no parallel backend), stops event propagation so it does not toggle the row expander, guards double-clicks, and only renders for running rows. The kill-failed path correctly resets the pending flag while success leaves the row to disappear via its terminal status event.

- **Merge conflict flag:** same overlap as #88783 - both PRs restructure this exact block in agents/index.tsx and touch the same i18n files; second merger rebases deliberately.