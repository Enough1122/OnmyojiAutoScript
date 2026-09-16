> AI code review — automated review; please use your judgment.

1. `apps/desktop/src/i18n/{ar,ja,zh,zh-hant}.ts` — all four non-English locales receive the **English strings verbatim** ("Manage folders", "No folders in this project.", "A project needs at least one folder") for six new keys — why it matters: every other user-visible key in those files is translated, so these render as jarring English islands in localized UIs, and nothing marks them as pending — suggestion: provide real translations now (they're short), or follow whatever convention exists for pending strings so a localization pass can find them.

2. `apps/desktop/src/app/chat/sidebar/project-dialog.tsx:~105–120` — the manage-folders add-folder lane hand-rolls a `setSubmitting/try/catch/notifyError` block that mirrors the adjacent `runSubmit` helper it sits next to — why it matters: duplicated error-handling will drift (e.g., `runSubmit` likely also closes the dialog or resets draft state on success) — suggestion: reuse `runSubmit` for this lane too, parameterizing the post-action behavior.

3. Nit (`hermes_cli/oneshot.py:~274–277`): the hint matches on ````"No access token found"```` substring plus a `relogin_required` attribute; if other auth failures phrase differently ("missing credentials", provider-specific text), they stay unhinted — consider routing through the same classifier that produces `FailoverReason.auth` if it's reachable here. Also worth noting in the PR body that ~90% of this diff is the manage-folders dialog feature while the title advertises the CLI hint — helps future archaeology.

The store-side `removeProjectFolder` is well built: client-side refusal below one folder, primary reassignment guarded by an existence check, tree-node path kept in sync when the removed folder was primary, optimistic set + `persistOrRollback` rollback matching the `addProjectFolder` pattern, and the dialog disables removal (with an explanatory tooltip) at exactly one folder.

— reviewer-a · automated agent review (Hermes week-review)
