> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

The core idea is right: `kanban_show` with no resolvable task id should orient (compact board listing + `hint`) rather than emit an env-var instruction a chat/orchestrator session can't act on (#91431), and letting `kanban_comment` inherit `HERMES_KANBAN_TASK` aligns it with every other lifecycle handler. The fallback payload is honest (`fallback` + `hint` keys, error dicts passed through untouched). Findings:

1. tools/kanban_tools.py:527 — direct functional conflict with open PR #91466: that PR makes the *same* code path (taskless `kanban_show`, `HERMES_KANBAN_TASK` unset) return a hard `task_id is required` error and adds tests asserting exactly that (`test_show_without_env_task_id_requires_param`), while this PR makes it return the board listing. Both also edit `tests/tools/test_kanban_tools.py`. Whichever lands second fails the other's tests. Maintainers need to pick one semantic (or scope #91466's requirement to dispatcher-worker contexts only) before merging either.

2. Diff hygiene — roughly two thirds of this diff is formatter churn (re-wrapped dicts/calls, blank-line insertion) riding along with two behavior changes and schema text changes. Please split formatting into its own commit (or PR); as-is it buries the real logic and makes bisect blame noisy.

3. tools/kanban_tools.py:2076 — dropping `task_id` from `required` fixes workers but silently weakens the contract for chat sessions: the model now learns about the requirement only from a runtime error after choosing `body` alone. The updated description mitigates this; consider strengthening it to "omit ONLY inside dispatcher-spawned workers" so agents in ordinary chats don't attempt the omission path at all.

4. tools/kanban_tools.py:705 — error-message drift: after this PR, `kanban_comment` says "Use kanban_list..." while complete/block/attach still say "(or set HERMES_KANBAN_TASK in the env)" — advice that's unactionable in exactly the non-worker contexts those messages reach. Cheap follow-up: unify all of them on the kanban_list wording.
