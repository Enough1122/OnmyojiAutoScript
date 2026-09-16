> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean tri-state contract: `path === null` is now reserved for Home's explicit no-workspace request (draft with `workspaceTarget: null`, **no** `session.create` fired), empty string keeps its legacy path-less-trunk fallback to the project root, and a real path stays an explicit target. `createBackendSessionForSend` maps null → omitted cwd so the backend never pins a Home tile to a repo, and both decisive tests — a Home tile opened while a *different* project scope is active, and startWorkspaceSession staying detached in the same situation — prove the scope can no longer hijack Home. Typing `NewChatWorkspaceTarget` through the draft callback keeps the null-vs-undefined distinction compiler-checked.
