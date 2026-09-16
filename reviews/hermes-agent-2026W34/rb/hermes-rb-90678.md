> AI code review — automated review for reference; please use your judgment.

The UX bug is real (a 3-row stub made older conversations unreachable from the overview) and aligning the client ceiling with the backend's `projects.tree` session window (2000) is the simplest fix. Two scaling concerns before this ships:

1. apps/desktop/src/store/projects.ts:~446 — `PROJECT_TREE_PREVIEW_LIMIT = 2000` applies to the *upfront* tree request for every project in the overview, and the all-profiles fan-out multiplies it by one database per profile. Payload size, JSON parse time, and store churn grow accordingly even when the user never expands anything. Consider requesting the small preview for collapsed rows and fetching the full window lazily on first expand — the expanded-row path already falls back to `latestProjectSessions(project, LIMIT)`, so an on-demand fetch slots in naturally.
2. apps/desktop/src/app/chat/sidebar/projects/overview-row.tsx:~105 — when a project genuinely has hundreds of sessions, expansion mounts that many `SidebarRowShell`s at once. The flat Recents list is virtualized; if these project rows are not, expanding a 2000-session project will hitch the sidebar thread. Either confirm the container is virtualized or gate full rendering behind the same windowing.
3. model.ts — `PROJECT_TREE_PREVIEW_LIMIT` kept its old name while its meaning changed from "preview count" to "full session window"; same for the `_EXPANDED_`/`_PREVIEW_` pair drifting apart in comments. Renaming to e.g. `PROJECT_TREE_SESSION_LIMIT` would stop the next reader from "fixing" it back to 3. (nit)
4. tests — the vitest mock gained the new constant, but nothing asserts that an expanded row renders more than the old stub of 3. One regression test with 5 fake sessions would pin the actual bug being fixed. (nit)

No blocking issues found.
