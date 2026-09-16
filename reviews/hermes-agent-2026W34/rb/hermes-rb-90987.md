> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Minimal and correctly scoped: gating \`profile_exists\` on \`not remove\` makes the cleanup path reachable exactly where it was dead (orphaned wrappers, the state doctor itself reports), while the safety argument is honestly delegated to \`remove_wrapper_script\`'s existing fail-closed properties — traversal-shaped names refused, and only files carrying the \`hermes -p\` marker are unlinked. The new tests prove all three corners that matter: orphan removal succeeds, a same-named non-wrapper file is *not* deleted (the arbitrary-file-delete regression this carve-out could have introduced), and the create path keeps its precondition.

Nit: when neither wrapper nor profile exists the CLI says "No alias 'demo' found to remove." — appending a pointer to \`hermes doctor\'s "Orphan alias" listing (the tool that surfaces these states) would close the discovery loop for users hitting #90983.

No blocking issues found.