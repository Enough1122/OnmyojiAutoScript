> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Sensible completion of the move-to-project flow: a "Home" escape hatch only appears when the session actually sits in a project, the implementation reuses the existing workspace.move RPC with `~` (backend-expanded), and the optimistic `$sessions` mirror + tree refresh match `moveSessionToProject`'s pattern. Two nits worth sweeping before merge — also note the new JSX block's indentation is off by one level and will trip the formatter:

1. apps/desktop/src/app/chat/sidebar/session-actions-menu.tsx:160 — `currentProjectId !== '__no_project__'` hard-codes the tree's Home sentinel string in the menu component; if the store ever renames its no-project marker, the Home item silently stops appearing (or appears for Home sessions). Export an `isHomeProjectId(id)` predicate (or the constant) from `@/store/projects` next to `projectIdForCwd` so the sentinel has one owner.
