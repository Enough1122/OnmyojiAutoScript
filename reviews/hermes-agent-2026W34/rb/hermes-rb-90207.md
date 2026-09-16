> AI code review — automated review for reference; please use your judgment.

Review of "feat(hermes-bots): make group activity live". Strong real-time plumbing overall: one stable per-member row updated in place, 120ms patch coalescing so heartbeats cannot churn renders, run-id + epoch fencing on every mutation, credential-shaped values redacted from tool previews before they reach the UI, and disciplined binding/timer teardown across finish, cancel, rename, and teardown paths. One likely functional bug plus two nits:

1. plugin.js — arity mismatch: settled/cancelled never land. updateGroupLiveRun takes (group, runId, mutate), but the event.kind === 'settled' and event.kind === 'cancelled' branches call it as updateGroupLiveRun(group, run => { ... }) — compare the previousRun branch, which passes runId correctly. With runId bound to the CALLBACK, the current.runId !== runId fence compares string vs function and always bails, so a live room NEVER transitions to settled or cancelled in the UI: rows keep spinning after the round ends until something else rebuilds the atom. Add the missing runId argument to both calls, and add a test that drives a settled event through applyGroupActivityToLive (the existing suite fences by epoch but apparently never exercises these two kinds).

2. Nit, preview redaction breadth — the credential regex catches token/api-key/secret/password/authorization/credential shapes; bearer-style JWTs pasted as bare eyJ-prefixed strings with no label slip through. Consider also masking any long high-entropy token-shaped run (32+ chars).

3. Nit, coalesce-map growth — the per-member token key (group + runId + memberKey joined by ':') accumulates one Map entry per member per run; bindings are pruned but the coalescedPatches/coalesceTimers maps rely on flush paths only — a member that goes silent mid-run leaves its timer entry until it fires (harmless at 120ms, but pairing the maps' lifecycle with the binding cleanup would be tidier).

The redaction-before-render and fenced-mutation design deserve credit — item 1 is the only thing I'd hold the merge for.
