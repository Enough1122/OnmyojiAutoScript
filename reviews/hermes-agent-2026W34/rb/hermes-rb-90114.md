> AI code review — automated review for reference; please use your judgment.

Complete feature slice: backend serves `archived_projects` alongside the tree (one RPC, no second round-trip), the desktop gets optimistic flip-with-rollback consistent with deleteProject, archiving an active project clears the selection, session grouping can't claim an archived project, older backends degrade to no-restore-UI rather than erroring, and all five locales got strings. Points:

1. apps/desktop/src/store/projects.ts:`archiveProject` (~925) — archiving the *active* project optimistically sets `$activeProjectId = null`, but confirm `snapshotProjects()` captures `$activeProjectId` too; if its rollback restores only projects/tree/archived lists, a failed archive leaves the selection cleared while everything else snaps back — asymmetric state after a rejected write. One line in the snapshot (or restoring it explicitly in the rollback path) closes it.
2. tui_gateway/server.py:_project_tree_inputs (~11112) — the archived list is built by calling `list_projects(conn, include_archived=True)` and filtering `p.archived` in Python, on top of the existing active-only `list_projects(conn)`. Two full project scans per tree build; fine at dashboard scale, but partitioning one include-archived query client-side would halve it. (nit)
3. sidebar/index.tsx:~652 — `archivedProjects` is forced to `[]` when `showAllProfiles` is true, so multi-profile users lose the restore affordance entirely. If that's deliberate (per-profile archives render under each profile scope), say so in a comment; otherwise render the section in all-profiles mode too. (nit)
4. The archived row's non-clickable design (restore is the only affordance) correctly encodes "no live workspace until restored" — good product thinking. (positive)

No blocking issues found.
