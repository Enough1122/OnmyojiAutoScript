> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Tidy feature: the focused-profile ranking lives in a pure, well-tested helper (seven unit cases covering normalization, ghost focus, default-first preservation, color stamping), the auto-reveal effect correctly no-ops when focus doesn't change (so a manual collapse survives same-profile refocuses), and lifting \`$focusedSessionProfile\` into \`session-states\` removes a private duplicate so the SDK host state and the sidebar read one source of truth. Header session-count badge answers the collapsed-glance question nicely.

Nit: two micro-points — (a) confirm \`setWorkspaceNodeOpen(profileKey, true)\` writes node state namespaced to the profile-grouping mode; if workspace open/closed state is shared across grouping modes, a project node that happens to share an id string would get expanded as a side effect; (b) in buildProfileGroups the \`groups.set(key, group)\` inside the loop is redundant (the Map already holds the mutated object reference).

No blocking issues found.