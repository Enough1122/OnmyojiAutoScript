> AI code review — automated review for reference; please use your judgment.

Correct and subtle ordering fix: stripping before `_merge_partial_save` was vacuous because the merge re-folds the on-disk document back in — so a stale managed leaf on disk survived the strip and persisted, waiting to become active the day the managed policy lifts. Moving the strip after the merge closes the resurrection path, the new test drives exactly the merge-sourced case (caller's dict never contained `model.default`) and pins both the file state and the stderr notice condition. Nothing to add.

— reviewer-b (automated review)

No blocking issues found.
