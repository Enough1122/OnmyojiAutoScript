> AI code review — automated review for reference; please use your judgment.

Right shape for the multi-agent-room echo problem: peers must be mentioned to count, each accepted peer round consumes a per-room budget that only an authorized *human* message refills, defaults are inert (no peers / budget 0), and invalid budgets fail closed to 0. The NO_REPLY abstention contract pushed into the session prompt keeps the turn in context without spamming the room — good design separation between gating and model behavior. Points:

1. plugins/platforms/matrix/adapter.py:~3467 — budget reset requires `sender in self._allowed_user_ids`. When no allowlist is configured (`_allowed_user_ids` empty = allow-all in this adapter's convention), `sender in set()` is always False, so the budget never resets after the first peer round and every later peer mention is dropped until restart. If empty-set-means-open is real here, gate the reset on "sender is an authorized OR unrestricted human" instead. A test with no MATRIX_ALLOWED_USERS would pin whichever semantics are intended.
2. Budget is keyed by room but shared across threads — activity in one thread exhausts another thread's peer rounds. Probably acceptable for v1; document it next to the config key. (nit)
3. A peer message that passes the mention+budget gates but is then rejected downstream (command parse failure, etc.) has already consumed a round. Minor accounting unfairness; noting only. (nit)
4. Confirm the NO_REPLY send-path filter lives in this PR (the adapter diff continues past what I can see) — if the gateway strips it, an unparsed NO_REPLY leaking verbatim into the room would be worse than the echo problem. One end-to-end test asserting the marker never reaches the adapter's send would close it.
5. The config-parsing tests covering list/comma-string forms and invalid budgets are exactly right. (positive)

No blocking issues found beyond item 1's open-room reset semantics.
