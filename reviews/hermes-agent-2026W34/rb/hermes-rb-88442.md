> AI code review — automated review for reference; please use your judgment.

Two well-motivated fixes in one PR, each solving a documented failure chain:

1. scripts/install.sh:`node_deps_workspace_args` — scoping the CLI npm install to ui-tui/web keeps apps/desktop's node-pty (no Linux prebuild → node-gyp → needs make/gcc) off CLI-only machines entirely, which is strictly better than warning about a toolchain those hosts don't have. The details are thought through: `--include-workspace-root` preserves the shared ESLint closure, missing-workspace fallback to `--workspaces=false` handles partial checkouts, and the comment cites the matching closure in `hermes update`. One question: `hermes update`'s `_update_node_dependencies` still does an unscoped install per its own path — should this PR align that call site too, or is update guaranteed to run where the desktop exists?
2. scripts/ci/classify_changes.py:`pull_request_changed_files` — recovering the file list from the pulls/files endpoint when a fork force-push 404s the compare API fixes a real "empty diff → ci_review=true → blocked" footgun, and correctly limits recovery to pull_request events so push/dispatch keep the old fail-open. The five-test matrix covers every branch including main()-level integration. (positive)
3. Minor: `pull_request_changed_files` shells out to `gh`, which must be present and authenticated on the runner — true for GitHub-hosted Actions, but worth one line in the docstring noting the dependency since classify_changes itself previously needed nothing but stdlib. (nit)
4. The install.sh test file name (`tests/test_install_sh_node_deps_workspaces.py`) suggests shell-function unit testing via extraction or source-grep — if it's source-grep based, note the usual drift caveat. (nit)

No blocking issues found.
