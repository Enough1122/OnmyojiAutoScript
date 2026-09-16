> AI code review — automated review for reference; please use your judgment.

The invariant is right — background reviews are daemon-flavored work that a process exiting at turn end can never collect — and wiring `_single_query_mode` through `_init_agent` plus gating the codex trigger is clean. The parametrized "review lifetime matches CLI lifetime" test names the contract exactly. One coverage gap and two nits:

1. hermes_cli/oneshot.py:476 — the oneshot builder constructs `AIAgent(...)` directly and does **not** pass `skip_background_review`, yet oneshot agents (kanban workers, scripted runs) are the most short-lived of all — they have exactly the same doomed-review problem this PR fixes for `chat -q`. Either pass the flag there too (it's hard to see when a one-shot *should* spawn one) or add a sentence to the PR explaining why those reviews are expected to complete.
2. agent/codex_runtime.py:913 — `getattr(agent, "skip_background_review", False)`: now that the constructor accepts the kwarg, prefer direct attribute access (`agent.skip_background_review`) so a future rename fails loudly instead of silently re-enabling doomed reviews via the getattr default.
3. cli_agent_setup_mixin.py:536 — `getattr(self, "_single_query_mode", False)` implies the attribute isn't guaranteed on every HermesCLI construction path; setting a class-level `_single_query_mode = False` default would make the mixin read self-documenting instead of defensive. (nit)

No blocking issues found.
