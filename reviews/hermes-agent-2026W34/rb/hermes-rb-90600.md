> AI code review — automated review; please use your judgment.

Genuinely user-protective change: the autostash only ever covered working-tree edits, so local *commits* were silently orphaned by the divergence `reset --hard` — branching `hermes-update-backup-*` at HEAD first gives them a durable, discoverable ref plus an actionable recovery line ("git rebase origin/main <backup>"). The zero-local-commits fast path keeps managed installs quiet, rev-list failure deliberately fails open (the refs just resolved for the failed ff-only, so treating a hiccup as "nothing to preserve" beats aborting recovery), and the tests drive **real git repos** through the exact diverged state and assert reachability *after* the reset runs — the right contract.

1. `hermes_cli/update_cmd.py:~192–199` — unlike its sibling `_capture_head_sha`, this helper doesn't guard `subprocess.run` against `OSError`; if git is momentarily unresolvable (PATH churn, exec-format edge), the update flow now dies here instead of degrading to today's behavior — why it matters: this runs inside recovery, where the bar for making things worse should be high — suggestion: catch `OSError` alongside the returncode checks and return `None` with the same warn-and-continue posture as the branch-creation failure path.

2. Nit (`:~206–208`): the timestamped name collides within the same second (docstring acknowledges it); appending the short SHA (````f"hermes-update-backup-%Y%m%d-%H%M%S-{head[:7]}"````) makes collisions impossible and self-describing. Relatedly, backup branches accumulate forever across many updates — consider pruning all but the most recent few, or documenting that cleanup is manual.

— reviewer-a · automated agent review (Hermes week-review)
