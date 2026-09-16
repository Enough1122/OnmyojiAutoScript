> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Excellent root-cause work: the repository stage body runs in a `set +e` subshell, so unguarded `git fetch`/`git checkout` failures fell through to "Repository ready" + exit 0 — an update that fetched nothing reported `{ok: true}`. The explicit guards fix that, the failure messages name the likely cause (github 429/transient), and `log_autostash_recovery` makes sure work stashed earlier in the update path is never silently abandoned mid-abort. The tests drive the *real* installer stage against a moved bare remote (a clean simulation of unreachable origin), asserting non-zero exit, named failure, stash survival + recovery hint with local changes, and no misfiring hint on clean checkouts.
