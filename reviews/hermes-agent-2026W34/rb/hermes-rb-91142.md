> AI code review — automated review for reference; please use your judgment.

1. `agent/kanban_stop.py:~112–116` (`dispatcher_worker_run_is_terminal`) — terminality is defined as `status != "running"`, so ANY future/unknown status value stops the worker's conversation loop — why it matters: if the schema ever grows a transitional state (`"retrying"`, `"handoff"`, `"paused"`), workers silently halt mid-task with no error anywhere; an explicit allow-set (````{"done", "failed", "cancelled", "blocked"}````) degrades new states to "keep going", which is the safe direction here — suggestion: invert the check to an explicit terminal set (the docstring's own examples already enumerate them).

2. `agent/conversation_loop.py:~7385–7398` — the run-row probe executes **after every successful tool batch** for every dispatcher-owned worker, even batches that touched no Kanban tool — why it matters: it's a cross-process SQLite read per iteration; cheap today, but the natural refinement is to gate on the executed batch containing a `kanban_*` tool call (names are right there), which also removes a redundant read after pure-inference turns — suggestion: optional micro-guard, not blocking.

3. `model_tools.py:~84–136` (`_configured_worker_kanban_tool_allowlist`) — solid gating (env + non-delegated + dispatcher-owned) and the always-retained terminal pair is exactly the right invariant; one gap: entries in `worker_tools` that name *non-Kanban* tools are silently ignored rather than warned — why it matters: a user listing `terminal_exec` there expects it to appear and will debug why it doesn't — suggestion: log one INFO line listing ignored non-`kanban_` names.

4. Nit (`conversation_loop.py:~7398`): ````"✓ Kanban worker terminal state recorded"```` is a hardcoded English status string in a codebase that otherwise localizes gateway-facing text — worth routing through i18n if this surfaces on localized clients.

Overall: the three mechanisms compose well — authoritative-run-row termination (with fail-open on read errors, correctly *not* stopping on failed `kanban_complete`), stop-nudge scoped to dispatcher-owned contexts so delegated children keep parent behavior, and a schema-shrink that cannot be configured into an unwinnable state. Strong test matrix including a genuine end-to-end loop-stop assertion. Item 1 is the only design question I'd settle pre-merge.

— reviewer-a · automated agent review (Hermes week-review)
