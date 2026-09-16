> AI code review — automated review for reference; please use your judgment.

Correct fix with careful race hygiene: the git-root resolution is sequence-guarded and cwd-stability-checked before landing in the store, every read path (`reviewCtx`, `absolutePath`, stage/unstage/revert) resolves against it, the loading flag is now also cleared on the detached-chat early return (a real forever-skeleton fix called out explicitly), and the root resets on close and repo-move. The subdirectory test drives both `gitRoot` resolution and subsequent list/diff calls against the top-level root. One nit:

- apps/desktop/src/store/review.ts:135 — nit — when `desktopGitRoot` fails, the pane silently degrades to cwd-relative behavior (the pre-fix bug) for that session; a one-line debug log would make "why is my review empty again" diagnosable.

No blocking issues found.

— reviewer-b (automated review)
